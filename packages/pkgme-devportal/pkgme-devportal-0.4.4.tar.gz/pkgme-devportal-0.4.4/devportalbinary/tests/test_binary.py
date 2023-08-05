# Copyright 2011-2012 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from contextlib import closing
import os
import shutil

from fixtures import TempDir
from testresources import ResourcedTestCase
from testtools import TestCase
from testtools.matchers import (
    SameMembers,
    StartsWith,
    )
from treeshape import (
    CONTENT,
    FileTree,
    PERMISSIONS,
    )

from devportalbinary.binary import (
    BinaryBackend,
    DEFAULT_EXTRA_RULES_TARGETS,
    find_bundled_libraries,
    get_file_type,
    get_file_types,
    get_packages_for_libraries,
    get_shared_library_dependencies,
    guess_dependencies,
    guess_embedded_libs_search_paths,
    guess_executable,
    guess_extra_debian_rules_targets,
    is_elf_exectuable,
    iter_binaries,
    iter_executables,
    needed_libraries_from_objdump,
    NoBinariesFound,
    OVERRIDE_DH_SHLIBDEPS_TEMPLATE,
    UnknownDependency,
    )
from devportalbinary.configuration import load_configuration
from devportalbinary.database import PackageDatabase
from devportalbinary.metadata import (
    MetadataBackend,
    )
from devportalbinary.testing import (
    BackendTests,
    BinaryFileFixture,
    DatabaseConfig,
    get_test_data_dir_path,
    get_test_data_file_path,
    LibsConfigSettings,
    MetadataFixture,
    postgres_db_resource,
    )


class TestObjDump(TestCase):

    def test_no_binaries(self):
        self.assertRaises(NoBinariesFound, needed_libraries_from_objdump, [])


class FindExecutableTests(TestCase):

    def test_only_one_file_and_it_is_executable(self):
        # If there is only one file and it's executable, find that.
        tree = FileTree({'some-file': {PERMISSIONS: 0755}})
        path = self.useFixture(tree).path
        executables = list(iter_executables(path))
        self.assertEqual(['some-file'], executables)

    def test_finds_elf_executable(self):
        # ELF executables are considered executables.
        executable = get_test_data_file_path('hello', 'hello')
        with open(executable, 'rb') as f:
            content = f.read()
        tree = FileTree({'some-file': {PERMISSIONS: 0644, CONTENT: content}})
        path = self.useFixture(tree).path
        executables = list(iter_executables(path))
        self.assertEqual(['some-file'], executables)

    def test_no_files_at_all(self):
        # iter_executables finds no executables if there are no files at all.
        path = self.useFixture(FileTree({})).path
        executables = list(iter_executables(path))
        self.assertEqual([], executables)

    def test_no_executable_files(self):
        # If there are no executable files, iter_executables returns None.
        tree = self.useFixture(FileTree({'some-file': {PERMISSIONS: 0644}}))
        executables = list(iter_executables(tree.path))
        self.assertEqual([], executables)

    def test_directory_is_not_executable_file(self):
        # A directory does not count as an executable file.
        tree = self.useFixture(FileTree({'directory/': {}}))
        executables = list(iter_executables(tree.path))
        self.assertEqual([], executables)

    def test_finds_executable_in_nested_directory(self):
        # Even if the file is in some nested directory, we are able to find
        # it.
        tree = {
            'directory/my-executable': {PERMISSIONS: 0755},
            }
        path = self.useFixture(FileTree(tree)).path
        executables = list(iter_executables(path))
        self.assertEqual(['directory/my-executable'], executables)

    def test_multiple_executables(self):
        # If there are many executables, iter_executables finds them all.
        tree = {
            'some-file': {PERMISSIONS: 0755},
            'another-file': {PERMISSIONS: 0755},
            }
        path = self.useFixture(FileTree(tree)).path
        executables = list(iter_executables(path))
        self.assertThat(
            executables, SameMembers(['another-file', 'some-file']))


class GuessExecutableTests(TestCase):

    def test_no_executables(self):
        # If there are no executables to select from, then return None,
        # indicating the fact.
        executable = guess_executable('package-name', iter([]))
        self.assertIs(None, executable)

    def test_only_one_executable(self):
        # If there's only one executable, then return that, since it's
        # probably the main executable for the package.
        executable = guess_executable('package-name', ['whatever'])
        self.assertEqual('whatever', executable)

    def test_exact_package_name_match(self):
        # If there are many executables, but one of them has the same name as
        # the package, then that is probably the main executable.
        executable = guess_executable(
            'package-name', ['whatever', 'package-name'])
        self.assertEqual('package-name', executable)

    def test_exact_package_name_match_in_subdir(self):
        # If there are many executables, but one of them has the same name as
        # the package, then that is probably the main executable, even if it
        # is in a sub-directory.
        executable = guess_executable(
            'package-name', ['whatever', 'subdir/package-name', 'foo'])
        self.assertEqual('subdir/package-name', executable)

    def test_multiple_exact_matches(self):
        # If there are many executables that have the same name as the
        # package, then the one that is the least nested is our best guess.
        executable = guess_executable(
            'package-name', [
                'whatever', 'a/b/c/d/e/subdir/package-name', 'foo',
                'subdir/package-name'])
        self.assertEqual('subdir/package-name', executable)

    def test_different_case_match(self):
        # If one of the executables has the same name as the package, but
        # spelled with different case, then that is our best guess.
        executable = guess_executable(
            'packagename', [
                'whatever', 'a/b/c/d/e/subdir/packagename', 'foo',
                'subdir/PackageName'])
        self.assertEqual('subdir/PackageName', executable)

    def test_many_executables(self):
        # If there are many executables, and their names have no particular
        # relationship to the package name, then just pick the top-most
        # one. If there's more than one, take the alphabetically sorted.
        executable = guess_executable(
            'package-name', ['dir/x', 'dir/sub/y', 'z', 'a'])
        self.assertEqual('a', executable)

    def test_fuzzy_mach(self):
        executable = guess_executable(
            'bittriprunner', ['install', 'bit.trip.runner/bit.trip.runner'])
        self.assertEqual('bit.trip.runner/bit.trip.runner', executable)


class GetFileTypeTests(TestCase):

    def test_plain_text(self):
        tree = {'foo.txt': {CONTENT: 'boring content\n'}}
        path = self.useFixture(FileTree(tree)).path
        file_type = get_file_type(os.path.join(path, 'foo.txt'))
        self.assertEqual('ASCII text', file_type)

    def test_data(self):
        file_type = get_file_type(
            get_test_data_file_path('data-file', 'foo.data'))
        self.assertEqual('data', file_type)

    def test_elf_binary(self):
        binary_path = get_test_data_file_path('hello', 'hello')
        file_type = get_file_type(binary_path)
        self.assertThat(file_type, StartsWith('ELF'))

    def test_elf_library(self):
        binary_path = get_test_data_file_path('simple', 'simple.so.1')
        file_type = get_file_type(binary_path)
        self.assertThat(file_type, StartsWith('ELF'))

    def test_multiple(self):
        tree = {'foo.txt': {CONTENT: 'boring content\n'}}
        path = self.useFixture(FileTree(tree)).path
        file_types = get_file_types(
            [os.path.join(path, 'foo.txt'),
             get_test_data_file_path('data-file', 'foo.data')])
        self.assertEqual(['ASCII text', 'data'], file_types)

    def test_no_files_given(self):
        self.assertEqual([], get_file_types([]))
        self.assertEqual([], get_file_types(iter([])))


class IterBinariesTests(TestCase):

    def test_no_binaries(self):
        path = self.useFixture(TempDir()).path
        self.assertEqual([], list(iter_binaries(path)))

    def test_some_binaries(self):
        path = get_test_data_dir_path('multi-binary')
        binaries = sorted(iter_binaries(path))
        self.assertEqual(
            [os.path.join(path, 'subdir', 'hello'),
             os.path.join(path, 'subdir', 'hello-missing-deps'),
             os.path.join(path, 'subdir', 'simple.so.1')],
            binaries)


class GetSharedLibraryDependenciesTests(TestCase):

    def test_get_shared_library_dependencies(self):
        hello = get_test_data_file_path('hello', 'hello')
        deps = get_shared_library_dependencies([hello])
        self.assertEqual((set(['libc.so.6']),  'i386'), deps)


class FindBundledLibrariesTests(TestCase):

    def test_find_bundlded_libraries_one_found(self):
        path = self.useFixture(TempDir()).path
        # pretend we have this libraries bundled in our path
        embedded_libnames = ["libfoo.so.1", "libbar.so.2"]
        for libname in embedded_libnames:
            with open(os.path.join(path, libname), "w"):
                pass
        # the libraries required by the mystical binary
        libraries_required = embedded_libnames + ["libc6.so.1", "libjml.so"]
        # ensure that its really found
        found = find_bundled_libraries(path, libraries_required)
        self.assertEqual(
            { "libfoo.so.1" : ["."], "libbar.so.2" : ["."]}, found)


class GuessDependenciesTests(TestCase, ResourcedTestCase):

    resources = [
        ('db_fixture', postgres_db_resource),
        ]

    def test_guess_dependencies(self):
        self.useFixture(DatabaseConfig(self.db_fixture))
        with closing(PackageDatabase(self.db_fixture.conn)) as db:
            db.update_package('eglibc', {'i386': {'libc.so.6': 'libc6'}})
        deps, arch = guess_dependencies(get_test_data_dir_path('hello'))
        self.assertEqual(set(['libc6']), deps)

    def test_guess_dependencies_error_on_unknown_dependency(self):
        self.useFixture(DatabaseConfig(self.db_fixture))
        e = self.assertRaises(UnknownDependency,
                guess_dependencies, get_test_data_dir_path('hello'))
        self.assertEqual('Can\'t find dependency for "libc.so.6".', str(e))


class GuessEmbeddedSearchPathsTests(TestCase):

    def test_guess_embedded_search_path(self):
        bundled_lib_test_dir = get_test_data_dir_path('bundled_library')
        paths = guess_embedded_libs_search_paths(bundled_lib_test_dir)
        self.assertEqual(set(["."]), paths)


class BinaryBackendTests(BackendTests, ResourcedTestCase):

    BACKEND = BinaryBackend

    resources = [
        ('db_fixture', postgres_db_resource),
        ]

    def setUp(self):
        super(BinaryBackendTests, self).setUp()
        self.useFixture(DatabaseConfig(self.db_fixture))

    def test_want_with_metadata_and_binaries(self):
        # If we detect a binary, then we score 10. The way we determine if
        # something is a binary is if it has a devportal-metadata.json in its
        # top-level.
        path = self.useFixture(MetadataFixture({})).path
        self.useFixture(BinaryFileFixture(path))
        self.assertEqual(
            {'score': 10,
             'reason': 'Has ELF binaries and a metadata file'},
            BinaryBackend.want(path))

    def test_want_with_just_metadata(self):
        # If something just has a metadata file but no binaries it is
        # not wanted
        path = self.useFixture(MetadataFixture({})).path
        self.assertEqual(
            {'score': 0,
             'reason': 'No ELF binaries found.'}, BinaryBackend.want(path))

    def test_description(self):
        # The binary backend uses the package description that's in the
        # metadata.
        expected_description = self.getUniqueString()
        backend = self.make_backend(
            metadata={MetadataBackend.DESCRIPTION: expected_description})
        description = backend.get_description()
        self.assertEqual(expected_description, description)

    def test_no_description(self):
        # If no description is provided in the metadata then the description
        # in the package info is just an empty string.
        backend = self.make_backend()
        description = backend.get_description()
        self.assertEqual('', description)

    def test_build_depends(self):
        # Make sure there's a database.
        backend = self.make_backend()
        shutil.copy(
            get_test_data_file_path('hello', 'hello'), backend.path)
        with closing(PackageDatabase(self.db_fixture.conn)) as db:
            db.update_package('eglibc', {'i386': {'libc.so.6': 'libc6'}})
        deps, arch = guess_dependencies(backend.path)
        expected_deps = ', '.join(deps)
        build_deps = backend.get_build_depends()
        self.assertEqual(expected_deps, build_deps)

    def test_depends(self):
        backend = self.make_backend()
        depends = backend.get_depends()
        self.assertEqual('${shlibs:Depends}, ${misc:Depends}', depends)

    def test_executable_is_best_guess(self):
        package_name = self.getUniqueString()
        executables = {
            'whatever/not-the-best': {PERMISSIONS: 0755},
            'this-one-is-best': {PERMISSIONS: 0755},
            }
        tempdir = self.useFixture(FileTree(executables))
        best = guess_executable(package_name, executables)
        backend = self.make_backend(tempdir.path)
        self.assertEqual(
            '/opt/%s/%s' % (package_name, best),
            backend.get_executable(package_name))

    def test_config_glue_lib_overrides(self):
        test_libs = {
            'libasound.so.2': 'libasound2',
            'libGL.so.1': 'libgl1-mesa-glx',
            'libfoo.so.2': 'libfoo',
            }
        self.useFixture(LibsConfigSettings(test_libs))
        conf = load_configuration()
        self.assertEqual(conf.options.libraries_overrides, test_libs)

    def test_get_lib_overrides_for_packages_for_libraries(self):
        # The configuration file overrides the found library dependencies.
        with closing(PackageDatabase(self.db_fixture.conn)) as db:
            db.update_package('foo', {'i386': {'libasound.so.2': 'libfoo'}})
        self.assertEqual(
            get_packages_for_libraries(["libasound.so.2"], "i386"),
            set(["libasound2"]))

    def test_architecture(self):
        # Check that the architecture reported for the package by the
        # backend matches the architecture that the binaries are built
        # for (in this case i386). This assumes that we don't multiarch
        # the package.
        path = self.useFixture(MetadataFixture({})).path
        self.useFixture(BinaryFileFixture(path))
        backend = self.make_backend(path)
        with closing(PackageDatabase(self.db_fixture.conn)) as db:
            db.update_package('eglibc', {'i386': {'libc.so.6': 'libc6'}})
        conf = load_configuration()
        self.assertEqual(backend.get_architecture(), "i386")

    def test_get_extra_targets_makes_executable_executable(self):
        package_name = 'package'
        executable_path = 'a/binary'
        path = self.getUniqueString()
        extra_targets = guess_extra_debian_rules_targets(package_name, path,
                lambda l: [], executable_path=executable_path)
        self.assertIn(
                "override_dh_fixperms:"
                "\n\tchmod u+x debian/{1}/{0}"
                "\n\tdh_fixperms -X/opt/".format(executable_path,
                    package_name),
                extra_targets)

    def test_get_extra_targets_no_bundled_libs(self):
        package_name = self.getUniqueString()
        path = self.getUniqueString()
        self.assertEqual(
            DEFAULT_EXTRA_RULES_TARGETS,
            guess_extra_debian_rules_targets(package_name, path, lambda l: []))

    def test_get_extra_targets_bundled_libs(self):
        package_name = "a-pkgname"
        path = self.getUniqueString()
        ld_search_path = ["x86/lib"]
        expected_ld_search_path = ("$(CURDIR)/debian/{package_name}"
                "/opt/{package_name}/{search_path}").format(package_name=package_name,
                        search_path=ld_search_path[0])
        self.assertEqual(
            DEFAULT_EXTRA_RULES_TARGETS+OVERRIDE_DH_SHLIBDEPS_TEMPLATE.format(
                ld_search_path=expected_ld_search_path),
            guess_extra_debian_rules_targets(
                package_name, path, lambda l: ld_search_path))

    def test_copyright_no_maintainer(self):
        metadata = self.make_metadata()
        backend = self.make_backend(metadata=metadata)
        expected = """\
Please see the individual files in this archive for the exact copyright holders.

This file was automatically generated.
"""
        self.assertEqual(expected, backend.get_explicit_copyright())

    def test_copyright_with_maintainer(self):
        metadata = self.make_metadata()
        submitter = 'Jonathan Lange <jml@mumak.net>'
        metadata[MetadataBackend.MAINTAINER] = submitter
        backend = self.make_backend(metadata=metadata)
        expected = """\
Please see the individual files in this archive for the exact copyright holders or contact the submitter of the application, %s.

This file was automatically generated.
""" % (submitter,)
        self.assertEqual(expected, backend.get_explicit_copyright())


class IsElfExecutableTests(TestCase):

    def test_not_elf(self):
        self.assertEqual(False, is_elf_exectuable('blah'))

    def test_not_executable(self):
        self.assertEqual(False,
                is_elf_exectuable('ELF 32-bit LSB shared object'))

    def test_executable(self):
        self.assertEqual(True,
                is_elf_exectuable('ELF 32-bit LSB executable'))

    def test_executable_with_extra_junk(self):
        self.assertEqual(True,
                is_elf_exectuable('ELF 32-bit LSB executable, blah'))

    def test_not_executable_with_extra_junk(self):
        self.assertEqual(False,
                is_elf_exectuable(
                    'ELF 32-bit LSB shared object, blah executable'))
