from collections import namedtuple
import os

from fixtures import TempDir
from storm.databases.postgres import psycopg2
from storm.exceptions import ClosedError
from testresources import ResourcedTestCase
from testtools import TestCase
from testtools.matchers import (
    Equals,
    Matcher,
    )
from treeshape import (
    CONTENT,
    FileTree,
    )

from devportalbinary.database import (
    AptFilePackageDatabase,
    deb_file_url_for_publication,
    dict_add,
    find_file_under_dir,
    get_dependency_database,
    get_file_contents,
    get_package_info_from_publication,
    is_library_package,
    LibdepServiceClient,
    libdep_mapping_from_symbols,
    load_configuration,
    NoSharedObject,
    possible_sonames_for_shared_object,
    PackageDatabase,
    publishings_to_package_info,
    shared_object_info_to_soname,
    shared_objects_from_shlibs,
    TooManySharedObjects,
    )
from devportalbinary.testing import (
    ConfigFileFixture,
    ConfigSettings,
    postgres_db_resource,
    )

from djlibdep.test_double import LibdepServiceDouble
from libdep_service_client.client import Client


class ResultsIn(Matcher):

    def __init__(self, db, rows):
        self._db = db
        self._rows = rows

    def match(self, query):
        # XXX: Abstraction violation
        results = self._db._store.execute(query)
        return Equals(self._rows).match(list(results))


class TestDatabase(TestCase, ResourcedTestCase):

    resources = [
            ('db_fixture', postgres_db_resource),
            ]

    def get_package_db(self):
        db = PackageDatabase(self.db_fixture.conn)
        self.addCleanup(db.close)
        return db

    def test_insert_new_library(self):
        db = self.get_package_db()
        db.insert_new_library('foo-src', 'libfoo.so.0', 'foo', 'i386')
        self.assertThat(
            "SELECT source_package_name, library, dependency, architecture FROM libdep",
            ResultsIn(db, [('foo-src', 'libfoo.so.0', 'foo', 'i386')]))

    def test_double_insert(self):
        db = self.get_package_db()
        db.insert_new_library('foo-src', 'libfoo.so.0', 'foo', 'i386')
        self.assertRaises(
            psycopg2.IntegrityError,
            db.insert_new_library, 'foo-src', 'libfoo.so.0', 'foo', 'i386')

    def test_differing_dependencies(self):
        db = self.get_package_db()
        db.insert_new_library('foo-src', 'libfoo.so.0', 'foo', 'i386')
        db.insert_new_library('foo-src', 'libfoo.so.0', 'bar', 'i386')
        deps = db.get_dependencies('libfoo.so.0')
        self.assertEqual(deps, set(['foo', 'bar']))

    def test_get_dependencies(self):
        db = self.get_package_db()
        db.insert_new_library('foo-src', 'libfoo.so.0', 'foo', 'i386')
        deps = db.get_dependencies('libfoo.so.0')
        self.assertEqual(deps, set(['foo']))

    def test_respects_architecture(self):
        db = self.get_package_db()
        db.insert_new_library('foo-src', 'libfoo.so.0', 'foo', 'i386')
        db.insert_new_library('foo-src', 'libfoo.so.0', 'foo-amd64', 'amd64')
        deps = db.get_dependencies('libfoo.so.0', arch='amd64')
        self.assertEqual(deps, set(['foo-amd64']))

    def test_unknown_library(self):
        db = self.get_package_db()
        deps = db.get_dependencies('libfoo.so.0')
        self.assertEqual(deps, set())

    def test_update_package(self):
        db = self.get_package_db()
        db.update_package(
            'foo', {'i386': {'libfoo.so.1': 'foo-bin'}})
        deps = db.get_dependencies('libfoo.so.1')
        self.assertEqual(deps, set(['foo-bin']))

    def test_update_existing_package_no_libraries(self):
        db = self.get_package_db()
        db.update_package('foo', {'i386': {'libfoo.so.1': 'foo-bin'}})
        # Run again, this time with no symbols, representing that a newer
        # version of the package no longer exports any libraries.
        db.update_package('foo', {'i386': {}})
        deps = db.get_dependencies('libfoo.so.1')
        self.assertEqual(deps, set())

    def test_update_package_two_architectures(self):
        # If two architectures are updated separately then they
        # shouldn't interfere
        db = self.get_package_db()
        db.update_package('foo', {'i386': {'libfoo.so.1': 'foo-bin'}})
        db.update_package('foo', {'amd64': {'libfoo.so.1': 'foo-bin-amd64'}})
        deps = db.get_dependencies('libfoo.so.1', arch='i386')
        self.assertEqual(deps, set(['foo-bin']))

    def test_close(self):
        # Test that we can close the package db.
        db = PackageDatabase(self.db_fixture.conn)
        db.close()
        self.assertRaises(ClosedError, db.insert_new_library, 'foo',
                'libfoo.so.1', 'foo-bin', 'i386')

    def test_close_twice(self):
        # Test that we can close the package db twice with no exception.
        db = PackageDatabase(self.db_fixture.conn)
        db.close()
        db.close()


class TestDatabaseConfiguration(TestCase):

    def use_database_config(self, **db_settings):
        return self.useFixture(ConfigSettings(('database', db_settings)))

    def test_get_db_info_from_config_sqlite(self):
        other_tempdir = self.useFixture(TempDir())
        expected_db_path = os.path.join(other_tempdir.path, 'db')
        self.use_database_config(db_type='sqlite', path=expected_db_path)
        options = load_configuration()
        self.assertRaises(ValueError, PackageDatabase.get_db_info_from_config,
                options)

    def test_default_create_no_config(self):
        nonexistent = self.getUniqueString()
        self.useFixture(ConfigFileFixture(nonexistent))
        self.assertIsInstance(
            get_dependency_database(), AptFilePackageDatabase)

    def test_default_create_empty_config(self):
        self.useFixture(ConfigSettings())
        self.assertIsInstance(
            get_dependency_database(), AptFilePackageDatabase)

    def test_remote_service(self):
        base_url = 'http://example.com/libdep-service/'
        self.use_database_config(db_type='libdep-service', base_url=base_url)
        db = get_dependency_database()
        self.assertIsInstance(db, LibdepServiceClient)
        self.assertEqual(base_url, db._client.base_url)

    def test_get_db_info_from_config_postgres(self):
        expected_username = self.getUniqueString()
        expected_password = self.getUniqueString()
        expected_host = self.getUniqueString()
        expected_port = self.getUniqueInteger()
        expected_db_name = self.getUniqueString()

        self.use_database_config(
            db_type='postgres',
            username=expected_username,
            password=expected_password,
            host=expected_host,
            port=expected_port,
            db_name=expected_db_name)
        options = load_configuration()
        uri = PackageDatabase.get_db_info_from_config(options)
        self.assertEqual(expected_db_name, uri.database)
        self.assertEqual(expected_port, uri.port)
        self.assertEqual(expected_host, uri.host)
        self.assertEqual(expected_password, uri.password)
        self.assertEqual(expected_username, uri.username)


class FakeBPPH(object):

    def __init__(self):
        self.archive = namedtuple(
                'Archive', 'web_link')('http://lp.net/archive')
        self.distro_arch_series = namedtuple(
                'DistroArchSeries', 'architecture_tag')('i386')
        self.binary_package_name = 'foo'
        self.binary_package_version = '1'
        self.architecture_specific = True


class TestDebFileUrlForPublication(TestCase):

    def test_get_url(self):
        bpph = FakeBPPH()
        expected_url = '%s/+files/%s_%s_%s.deb' % (
            bpph.archive.web_link,
            bpph.binary_package_name,
            bpph.binary_package_version,
            bpph.distro_arch_series.architecture_tag,
            )
        self.assertEqual(expected_url, deb_file_url_for_publication(bpph))

    def test_get_url_with_epoch(self):
        # epochs are stripped from the version number
        bpph = FakeBPPH()
        bpph.binary_package_version = '1:1'
        expected_url = '%s/+files/%s_%s_%s.deb' % (
            bpph.archive.web_link,
            bpph.binary_package_name,
            '1',
            bpph.distro_arch_series.architecture_tag,
            )
        self.assertEqual(expected_url, deb_file_url_for_publication(bpph))

    def test_get_url_for_arch_indep(self):
        # epochs are stripped from the version number
        bpph = FakeBPPH()
        bpph.architecture_specific = False
        expected_url = '%s/+files/%s_%s_all.deb' % (
            bpph.archive.web_link,
            bpph.binary_package_name,
            '1',
            )
        self.assertEqual(expected_url, deb_file_url_for_publication(bpph))


class TestShlibs(TestCase):

    def test_empty(self):
        self.assertEqual({}, shared_objects_from_shlibs(""))

    def test_comments(self):
        self.assertEqual({}, shared_objects_from_shlibs("# aaaaa\n"))

    def test_blank_line(self):
        self.assertEqual({}, shared_objects_from_shlibs("\n"))

    def test_whitespace_line(self):
        self.assertEqual({}, shared_objects_from_shlibs("  \n"))

    def test_udeb_skipped(self):
        self.assertEqual({},
                shared_objects_from_shlibs("udeb: libfoo 1 libfoo\n"))

    def test_simple_soname(self):
        self.assertEqual({('libfoo', '1'): 'libfoo'},
                shared_objects_from_shlibs("libfoo 1 libfoo\n"))

    def test_other_type_of_soname(self):
        self.assertEqual({('libfoo', '4.8'): 'libfoo'},
                shared_objects_from_shlibs("libfoo 4.8 libfoo\n"))


class TestPossibleSonamesForSharedObject(TestCase):

    def test_no_dot(self):
        self.assertEqual(
            set(['libfoo.so.1', 'libfoo-1.so']),
            possible_sonames_for_shared_object('libfoo', '1'))

    def test_dot(self):
        self.assertEqual(
            set(['libfoo-1.0.so']),
            possible_sonames_for_shared_object('libfoo', '1.0'))


class TestFindFileUnderDir(TestCase):

    def test_file_missing(self):
        tree = {}
        path = self.useFixture(FileTree(tree)).path
        self.assertEqual(None, find_file_under_dir('nothere', path))

    def test_file_in_basedir(self):
        filename = 'here'
        tree = {filename: {}}
        built_tree = self.useFixture(FileTree(tree))
        self.assertEqual(built_tree.join(filename),
                find_file_under_dir(filename, built_tree.path))

    def test_file_in_subdir(self):
        filename = 'here'
        relpath = 'there/' + filename
        tree = {relpath: {}}
        built_tree = self.useFixture(FileTree(tree))
        self.assertEqual(built_tree.join(relpath),
                find_file_under_dir(filename, built_tree.path))

    def test_handles_multiple_matches(self):
        filename = 'here'
        relpath = 'there/' + filename
        tree = {filename: {}, relpath: {}}
        built_tree = self.useFixture(FileTree(tree))
        self.assertEqual(built_tree.join(filename),
                find_file_under_dir(filename, built_tree.path))


class TestSharedObjectInfoToSoname(TestCase):

    def test_no_files(self):
        tree = {}
        path = self.useFixture(FileTree(tree)).path
        self.assertRaises(NoSharedObject,
                shared_object_info_to_soname, 'libfoo', '1', path)

    def test_too_many_files(self):
        libname = 'libfoo'
        version = '1'
        possible_sonames = possible_sonames_for_shared_object(libname, version)
        tree = dict((name, {}) for name in possible_sonames)
        path = self.useFixture(FileTree(tree)).path
        self.assertRaises(TooManySharedObjects,
                shared_object_info_to_soname, libname, version, path)

    def test_file_found(self):
        libname = 'libfoo'
        version = '1'
        expected_soname = '{0}.so.{1}'.format(libname, version)
        tree = {expected_soname: {}}
        path = self.useFixture(FileTree(tree)).path
        self.assertEqual(expected_soname,
                shared_object_info_to_soname(libname, version, path))


class TestDictAdd(TestCase):

    def test_no_dicts(self):
        self.assertEqual({}, dict_add())

    def test_one_dict(self):
        self.assertEqual(dict(a=1), dict_add(dict(a=1)))

    def test_two_dicts(self):
        self.assertEqual(dict(a=1, b=2), dict_add(dict(a=1), dict(b=2)))

    def test_precedence(self):
        self.assertEqual(dict(a=2), dict_add(dict(a=1), dict(a=2)))


class TestIsLibraryPackage(TestCase):

    def test_lib_filename(self):
        self.assertEqual(True,
                is_library_package('http://launchpad.net/libfoo.deb'))

    def test_whitelisted(self):
        self.assertEqual(True,
                is_library_package('http://launchpad.net/zlib1g.deb'))

    def test_other(self):
        self.assertEqual(False,
                is_library_package('http://launchpad.net/bzr.deb'))


class TestGetPackageInfoFromPublication(TestCase):

    def test_returns_url_and_arch(self):
        bpph = FakeBPPH()
        self.assertEqual(
            (deb_file_url_for_publication(bpph),
                bpph.distro_arch_series.architecture_tag),
            get_package_info_from_publication(bpph))


class TestPublishingsToPackageInfo(TestCase):

    def test_integration(self):
        # This function is split out as it is the testable part of
        # fetch symbols files. This tests that the functions glue
        # together
        publishings = [FakeBPPH(), FakeBPPH()]
        expected_bpph = publishings[1]
        expected_bpph.binary_package_name = 'libfoo'
        expected_info = (deb_file_url_for_publication(expected_bpph),
                expected_bpph.distro_arch_series.architecture_tag)
        self.assertEqual([expected_info],
                publishings_to_package_info(publishings))


class TestGetFileContents(TestCase):

    def test_exists(self):
        expected_content = 'boring content\n'
        filename = 'foo.txt'
        tree = {filename: {CONTENT: expected_content}}
        path = self.useFixture(FileTree(tree)).join(filename)
        self.assertEqual(expected_content, get_file_contents(path))

    def test_not_exists(self):
        tree = {}
        path = self.useFixture(FileTree(tree)).join('nothere')
        self.assertEqual(None, get_file_contents(path))

    def test_directory(self):
        tree = {}
        path = self.useFixture(FileTree(tree)).path
        self.assertRaises(IOError, get_file_contents, path)


class TestLibdepMappingFromSymbols(TestCase):

    def test_empty(self):
        self.assertEqual({}, libdep_mapping_from_symbols(''))

    def test_blank_line_ignored(self):
        self.assertEqual({}, libdep_mapping_from_symbols('\n'))

    def test_alternate_template_ignored(self):
        self.assertEqual({}, libdep_mapping_from_symbols('| foo\n'))

    def test_meta_information_ignored(self):
        self.assertEqual({}, libdep_mapping_from_symbols('* foo\n'))

    def test_symbols_ignored(self):
        self.assertEqual({}, libdep_mapping_from_symbols(' foo\n'))

    def test_comments_ignored(self):
        self.assertEqual({}, libdep_mapping_from_symbols('# foo\n'))

    def test_include_ignored(self):
        self.assertEqual({},
                libdep_mapping_from_symbols('(arch=!armel)#include foo\n'))

    def test_includes_mapping(self):
        self.assertEqual({'libfoo.so.1': 'libfoo'},
                libdep_mapping_from_symbols('libfoo.so.1 libfoo #MINVER#\n'))


class TestLibdepServiceClient(TestCase):

    TEST_DATA = [('libfoo', {'i386': {'libfoo': 'libfoo-bin'}})]

    def test_wraps_libdep_service(self):
        double = self.useFixture(LibdepServiceDouble(self.TEST_DATA))
        client = Client(double.base_url)
        wrapper = LibdepServiceClient(client)
        self.assertEqual(
            {'libfoo': ['libfoo-bin']},
            wrapper.get_dependencies(['libfoo'], 'i386'))
