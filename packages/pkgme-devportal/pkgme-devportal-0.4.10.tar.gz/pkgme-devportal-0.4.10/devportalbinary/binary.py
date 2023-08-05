# Copyright 2011-2012 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Things to help package binary tarballs.

HIGHLY EXPERIMENTAL. USE AT YOUR OWN PERIL.

At the moment, we are assuming a great many things about these binary
tarballs.

* That they represent some sort of application to be run from an Ubuntu
  desktop

* Specifically, that although they might have many executables, only one is
  the "main executable" mentioned in the 'desktop' file

* They are written in C or C++ and that all dependencies can be determined
  by inspecting the included object files

* That the entire contents of the tarball can be copied into
  /opt/<package-name> and run from there

* That we have a metadata file, called 'devportal-metadata.json', in JSON.
  See ``MetadataBackend``.

The expectation is that this metadata file is generated from the developer
portal.
"""

__all__ = [
    'BinaryBackend',
    'guess_executable',
    'iter_executables',
   ]


from contextlib import closing
import os
import subprocess

from pkgme.errors import PkgmeError
from pkgme.run_script import run_subprocess
from pkgme import trace

from devportalbinary.configuration import load_configuration
from devportalbinary.database import get_dependency_database
from devportalbinary.metadata import (
    make_all_info_fn,
    make_want_fn,
    MetadataBackend,
    )


OVERRIDE_DH_STRIP_TEMPLATE = """
override_dh_strip:
\t# pkgme-binary does not call dh_strip as this may break binary-only apps
"""

# the overrides template for a dh_shlibdeps
OVERRIDE_DH_SHLIBDEPS_TEMPLATE = """
override_dh_shlibdeps:
\tdh_shlibdeps -l{ld_search_path}
"""

OVERRIDE_DH_FIXPERMS_TEMPLATE = """
override_dh_fixperms:
\tchmod u+x debian/{package_name}/{executable_path}
\tdh_fixperms -X/opt/
"""

# the default extra debian/rules targets
DEFAULT_EXTRA_RULES_TARGETS = OVERRIDE_DH_STRIP_TEMPLATE


class NoBinariesFound(PkgmeError):
    """Raised when we cannot find any binaries to examine for dependencies.
    """


class UnknownDependency(PkgmeError):
    """Raised when we do not know which dependency to add."""


class UnsupportedArchitecture(PkgmeError):
    """Raised when we find a unsupported architecture."""


class MixingArchitecturesNotSupported(PkgmeError):
    """Raised when there are different architectures in one tarball.

    Currently this binary backend can only find dependencies for one
    architecture in a given directory. If the directory contains e.g.
    both amd64/i386 binaries it needs to be submited as two different
    files.
    """


# This code is taken from:
#   http://code.activestate.com/recipes/576874-levenshtein-distance/
# (MIT licensed)
def levenshtein(s1, s2):
    """Calculate the Levenshtein distance from s1 to s2.

    The Levenshtein distance is the minimum number of edits needed to
    transform one string into the other, with the allowable edit operations
    being insertion, deletion, or substitution of a single character.

    The smaller the distance, the more "similar" the strings are.
    """
    l1 = len(s1)
    l2 = len(s2)

    matrix = [range(l1 + 1)] * (l2 + 1)
    for zz in range(l2 + 1):
        matrix[zz] = range(zz,zz + l1 + 1)
    for zz in range(0,l2):
        for sz in range(0,l1):
            if s1[sz] == s2[zz]:
                matrix[zz+1][sz+1] = min(matrix[zz+1][sz] + 1,
                                         matrix[zz][sz+1] + 1,
                                         matrix[zz][sz])
            else:
                matrix[zz+1][sz+1] = min(matrix[zz+1][sz] + 1,
                                         matrix[zz][sz+1] + 1,
                                         matrix[zz][sz] + 1)
    return matrix[l2][l1]


def _rank_executable(package_name, executable):
    """Rank ``executable`` as the main executable for ``package_name``.

    :return: Something, anything, that can be used as a sort key.  Lower means
        more likely to be the main executable.
    """

    def score_levenshtein(name):
        return levenshtein(package_name.lower(), name.lower())

    def score_path(executable):
        # The deeper the path, the less likely it is to be the one.
        return executable.count('/')

    name = os.path.basename(executable)
    # The alpha-sorting of the base name is a tie-breaker.
    return (
        score_levenshtein(name),
        score_path(executable),
        name,
        )


def guess_executable(package_name, executables):
    """
    From a list of executables, guess which one is likely to be the main
    executable.
    """

    def rank(executable):
        # Currying _rank_executable.
        return _rank_executable(package_name, executable)

    try:
        return sorted(executables, key=rank)[0]
    except IndexError:
        return None


def is_elf_exectuable(file_type):
    """Whether `file_type` indicates an ELF executable."""
    if file_type.startswith('ELF'):
        if "executable" in file_type.split(",")[0]:
            return True
    return False


def iter_executables(path):
    """Iterate through all executable files under 'path'.

    Paths yielded will be relative to 'path'. Directories will *not* be
    yielded. A file is considered "executable" if it has the executable
    bit set, or if it is an ELF executable.
    """
    for root, dirs, files in os.walk(path):
        for filename in files:
            file_path = os.path.join(root, filename)
            if (os.access(file_path, os.X_OK)
                    or is_elf_exectuable(get_file_type(file_path))):
                yield os.path.relpath(file_path, path)


def get_file_type(path):
    return get_file_types([path])[0]


def get_file_types(paths):
    paths = list(paths)
    if not paths:
        return []
    cmd = ['file', '-b'] + paths
    return subprocess.Popen(
        cmd, stdout=subprocess.PIPE).communicate()[0].splitlines()


OBJDUMP = '/usr/bin/objdump'
# Map the objdump "architecture" value to the dpkg architecture,
# objdump report i386 as "i386" but amd64 as "i386:x86-64" 
OBJDUMP_MAPPING = {
    "i386:x86-64" : "amd64",
}

def needed_libraries_from_objdump(binary_paths):
    binary_paths = list(binary_paths)
    if not binary_paths:
        raise NoBinariesFound()
    conf = load_configuration()
    cmd = [OBJDUMP, '-f', '-p'] + binary_paths
    output = run_subprocess(cmd)
    libraries = {}
    architecture = None
    last_line_was_blank = True
    for line in output:
        this_line_blank = (line.strip() == '')
        if last_line_was_blank and this_line_blank:
            try:
                current_binary = binary_paths.pop(0)
            except IndexError:
                break
            libraries[current_binary] = []
        if line.startswith('  NEEDED'):
            soname = line.split()[1]
            libraries[current_binary].append(soname)
        elif line.startswith('architecture: '):
            objdump_architecture = line.partition(":")[2].partition(",")[0].strip()
            dpkg_architecture = OBJDUMP_MAPPING.get(
                objdump_architecture, objdump_architecture)
            # at this point we only support a single architecture in the
            # entire package
            if architecture is not None and dpkg_architecture != architecture:
                raise MixingArchitecturesNotSupported(
                    "Found architecture '%s' for '%s' but also found "
                    "architecture '%s' earlier. Only a single architecture "
                    "at a time is supported." % (
                        dpkg_architecture, current_binary, architecture))
            # this is our architecture
            architecture = dpkg_architecture
            if architecture not in conf.architectures_supported:
                raise UnsupportedArchitecture(
                    "Can not handle '%s'" % architecture)
        last_line_was_blank = this_line_blank
    return libraries, architecture


def get_shared_library_dependencies(paths):
    """Find all of the shared libraries depended on the ELF binaries in 'paths'.
    """
    so_names = set()
    libraries, arch = needed_libraries_from_objdump(paths)
    for libs in libraries.values():
        for name in libs:
            so_names.add(name)
    return so_names, arch


def iter_binaries(path):
    """Find all of the ELF binaries underneath 'path'."""

    def is_binary(file_type):
        return file_type.startswith('ELF')

    for root, dirs, files in os.walk(path):
        paths = [os.path.join(root, filename) for filename in files]
        types = get_file_types(paths)
        for file_path, file_type in zip(paths, types):
            if is_binary(file_type):
                yield file_path


def get_packages_for_libraries(library_names, arch):
    conf = load_configuration()
    lib_overrides = conf.libraries_overrides
    with closing(get_dependency_database()) as db:
        deps = set()
        for lib in library_names:
            # ensure that overrides always "trump" the existing set if they
            # are found
            # XXX: we don't consider arch in overrides, do we need to?
            # -- james_w
            if lib in lib_overrides:
                new_deps = set([lib_overrides[lib]])
                trace.log(
                    "found dependencies '%s' for lib '%s' via override" % (
                        new_deps, lib))
            else:
                new_deps = db.get_dependencies(lib, arch)
                trace.log(
                    "found dependencies '%s' for lib '%s'" % (new_deps, lib))

            if not new_deps:
                raise UnknownDependency('Can\'t find dependency for "%s".' % lib)
            deps |= new_deps
        return deps


def find_bundled_libraries(path, libraries):
    """Find the directories that contain bundled library paths

    Returns a dict that maps the library name to the relative path
    (relative to the root 'path') where the library is found.
    """
    libraries_to_path = {}
    for dirpath, dirname, filenames in os.walk(path):
        for libname in list(libraries):
            if libname in filenames:
                lib_path = os.path.relpath(dirpath, path)
                if not libname in libraries_to_path:
                    libraries_to_path[libname] = []
                libraries_to_path[libname].append(lib_path)
    return libraries_to_path


def guess_embedded_libs_search_paths(
    path,
    library_finder=needed_libraries_from_objdump,
    libraries_to_deps=get_packages_for_libraries):
    binaries = iter_binaries(path)
    libraries, arch = get_shared_library_dependencies(binaries)
    libraries_to_paths = find_bundled_libraries(path, libraries)
    # the values are a list of lists of paths, so we need to "flatten" it
    # here
    paths = set([
        path for pathlist in libraries_to_paths.values() for path in pathlist])
    return paths


def guess_extra_debian_rules_targets(
    package_name,
    path,
    embedded_libs_finder=guess_embedded_libs_search_paths,
    executable_path=None):
    embedded_paths = embedded_libs_finder(path)
    extra_targets = DEFAULT_EXTRA_RULES_TARGETS
    if embedded_paths:
        base_dir = "$(CURDIR)/debian/{package_name}/opt/" \
            "{package_name}/".format(package_name=package_name)
        ld_search_path = build_ld_library_search_path(
            base_dir, embedded_paths)
        extra_targets += OVERRIDE_DH_SHLIBDEPS_TEMPLATE.format(
            ld_search_path=ld_search_path)
    if executable_path:
        extra_targets += OVERRIDE_DH_FIXPERMS_TEMPLATE.format(
                executable_path=executable_path,
                    package_name=package_name)
    return extra_targets


def guess_dependencies(
    path,
    library_finder=needed_libraries_from_objdump,
    libraries_to_deps=get_packages_for_libraries):
    binaries = iter_binaries(path)
    libraries, arch = get_shared_library_dependencies(binaries)
    # find/filter out the embedded libs
    libraries_to_paths = find_bundled_libraries(path, libraries)
    libraries = set(libraries) - set(libraries_to_paths.keys())
    # go over the rest
    deps = libraries_to_deps(libraries, arch)
    return deps, arch


def print_dependencies():
    deps = guess_dependencies('.')
    for dep in deps:
        print dep
    return 0


def print_executable():
    cwd = os.getcwd()
    print guess_executable(os.path.dirname(cwd), iter_executables(cwd))
    return 0


def build_ld_library_search_path(basedir, relative_dirs):
    """Return a string suitable for the LD_LIBRARY_PATH variable"""
    return os.pathsep.join(
        ["%s%s" % (basedir, p) for p in relative_dirs])


class BinaryBackend(MetadataBackend):
    """A backend that uses MyApps metadata to build a package for a binary."""

    # 8 out of 10 debian packagers say they use ${misc:Depends} to keep
    # their teeth shiny bright
    DEPENDS = '${shlibs:Depends}, ${misc:Depends}'

    def get_architecture(self):
        deps, architecture = guess_dependencies(self.path)
        return architecture

    def get_build_depends(self):
        deps, architecture = guess_dependencies(self.path)
        return ', '.join(deps)

    def get_depends(self):
        return self.DEPENDS

    def get_executable(self, package_name):
        executable = guess_executable(package_name, iter_executables(self.path))
        return '/opt/%s/%s' % (package_name, executable)

    def get_explicit_copyright(self):
        # See https://bugs.launchpad.net/pkgme-devportal/+bug/1026121/.
        maintainer = self.get_maintainer()
        if maintainer:
            maintainer_suffix = (
                " or contact the submitter of the application, %s" % (
                    maintainer,))
        else:
            maintainer_suffix = ''
        return """\
Please see the individual files in this archive for the exact copyright holders%s.

This file was automatically generated.
""" % (maintainer_suffix,)

    def get_extra_targets(self, package_name):
        executable_path = self.get_executable(package_name)
        return guess_extra_debian_rules_targets(package_name, self.path,
                executable_path=executable_path)

    @classmethod
    def want_with_metadata(cls, path, metadata):
        # XXX: should it also check that there is an executable?
        if list(iter_binaries(path)):
            return {
                'score': 10,
                'reason': 'Has ELF binaries and a metadata file'}
        else:
            return {'score': 0, 'reason': 'No ELF binaries found.'}


want = make_want_fn(BinaryBackend)
all_info = make_all_info_fn(BinaryBackend)
