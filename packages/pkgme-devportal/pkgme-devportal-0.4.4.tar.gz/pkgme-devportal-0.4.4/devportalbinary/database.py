# Copyright 2011 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from contextlib import closing, contextmanager
import errno
from itertools import chain
import os
import shutil
import tempfile

from bzrlib import urlutils
from fixtures import (
    Fixture,
    TempDir,
    )

from launchpadlib import (
    uris,
    )
from launchpadlib.launchpad import Launchpad
from pkgme.run_script import run_subprocess
from storm.locals import create_database, Store
from storm.uri import URI as StormURI

from .aptfile import AptFilePackageDatabase
from .configuration import (
    CONF_FILE_ENV_VAR,
    get_config_file_path,
    load_configuration,
    )
from .utils import download_file


# XXX: Historic name of this package.  Update to 'pkgme-devportal' and
# re-authorize.
APPLICATION_NAME = 'pkgme-binary'
SERVICE_ROOT = uris.LPNET_SERVICE_ROOT

SHLIBS_FILENAME = 'shlibs'
SYMBOLS_FILENAME = 'symbols'


# A list of package names that don't match lib*, but which we want
# to scan anyway.
PACKAGE_NAME_WHITELIST = [
    "e2fslibs",
    "odbcinst1debian2",
    "python2.7-dbg",
    "uno-libs3",
    "zlib1g",
    ]


def is_library_package(url):
    """Is ``url`` likely to contain libraries?"""
    filename = os.path.splitext(urlutils.basename(url))[0]
    if filename.startswith('lib'):
        return True
    for prefix in PACKAGE_NAME_WHITELIST:
        if filename.startswith(prefix):
            return True
    return False


class LaunchpadFixture(Fixture):

    def __init__(self, application_name, service_root):
        super(LaunchpadFixture, self).__init__()
        self._app_name = application_name
        self._service_root = service_root

    def setUp(self):
        super(LaunchpadFixture, self).setUp()
        tempdir = self.useFixture(TempDir())
        self.anonymous = Launchpad.login_anonymously(
            self._app_name, self._service_root, tempdir.path)


def iter_published_binaries(lp, since=None, name=None, exact_match=True):
    architectures = load_configuration().options.architectures_supported
    ubuntu = lp.distributions['ubuntu']
    archive = ubuntu.main_archive
    # XXX: oneiric is a puppy that is just for christmas. Specifically, it's a
    # bug that this is looking in oneiric, should instead be looking in
    # ... well, we don't know.
    oneiric = ubuntu.getSeries(name_or_version='oneiric')
    our_series = (
        oneiric.getDistroArchSeries(archtag=tag) for tag in architectures)
    filters = dict(status='Published')
    if since:
        filters['created_since_date'] = since
    if name:
        filters['binary_name'] = name
    filters['exact_match'] = exact_match
    return chain(
        *[archive.getPublishedBinaries(distro_arch_series=series, **filters)
          for series in our_series])


def possible_sonames_for_shared_object(libname, version):
    """Return the possible sonames gives info about a shared object.

    :return: a set of candidate sonames (as strings).
    """
    candidates = set(['{0}-{1}.so'.format(libname, version)])
    if '.' not in version:
        candidates.add('{0}.so.{1}'.format(libname, version))
    return candidates


def find_file_under_dir(filename, directory):
    """Find `filename` under `directory`.

    :return: the path of the first matching file, or None if the file
        wasn't found.
    """
    for dirpath, dirnames, filenames in os.walk(directory):
        if filename in filenames:
            return os.path.join(dirpath, filename)


class NoSharedObject(Exception):

    def __init__(self, libname, version, candidates):
        super(NoSharedObject, self).__init__(
            "No shared object matching {0} {1} could be found, "
            "looked for {2}".format(libname, version, candidates))


class TooManySharedObjects(Exception):

    def __init__(self, libname, version, candidates):
        super(TooManySharedObjects, self).__init__(
            "Too many objects matching {0} {1} could be found, "
            "found {2}".format(libname, version, candidates))



def shared_object_info_to_soname(libname, version, directory):
    """Resolve a (libname, version) tuple to a soname.

    Using the files from a package decide on the soname that
    the shared object info refers to. E.g. if the info is ("libfoo", "1")
    and there is a file named "libfoo.so.1" then that is the soname.

    :param directory: a directory of files to use to resolve.
    :return: the soname as a string
    :raises NoSharedObject: if a file corresponding to the info can't be
        found.
    :raises TooManySharedObjects: if multiple files matching the shared object
        info in different ways are found (mutliple files matching in
        the same manner are ignored.)
    """
    candidates = possible_sonames_for_shared_object(libname, version)
    files = {soname: find_file_under_dir(soname, directory) for soname in  candidates}
    found_files = dict(filter(lambda (x, y): y is not None, files.items()))
    if len(found_files) < 1:
        raise NoSharedObject(libname, version, candidates)
    elif len(found_files) > 1:
        raise TooManySharedObjects(libname, version, found_files.values())
    return found_files.keys()[0]



def libdep_mapping_for_deb(deb_file):
    """Returns the library -> dependency mapping information from a package.

    The symbols file will be read in preference to the shlibs file.
    If neither is present an empty dict will be returned indicating
    that there are no libraries.

    If there are libraries the dict will map from the library names
    to the package dependencies that should be used to get the
    library, e.g.

        {'libfoo.so.1': 'libfoo1', ...}
    """
    with extract_deb_control(deb_file) as control_dir:
        # Try symbols
        symbols_path = os.path.join(control_dir, SYMBOLS_FILENAME)
        symbols = get_file_contents(symbols_path)
        if symbols is not None:
            return libdep_mapping_from_symbols(symbols)

        # Try shlibs
        shlibs_path = os.path.join(control_dir, SHLIBS_FILENAME)
        shlibs = get_file_contents(shlibs_path)
        if shlibs is not None:
            shared_object_mapping = shared_objects_from_shlibs(shlibs)
            if shared_object_mapping:
                with extract_deb_content(deb_file) as deb_content:
                    def resolve_shared_objects(map_entry):
                        (libname, version), dependency = map_entry
                        soname = shared_object_info_to_soname(libname, version,
                                deb_content)
                        return soname, dependency
                    return dict(
                            map(resolve_shared_objects,
                                shared_object_mapping.items())
                            )
        return {}


def deb_file_url_for_publication(bpph):
    """Get the download URL for a binary package."""
    version = bpph.binary_package_version
    if ':' in version:
        version = version[version.index(':')+1:]
    arch = bpph.distro_arch_series.architecture_tag
    if not bpph.architecture_specific:
        arch = 'all'
    return '%s/+files/%s_%s_%s.deb' % (
        bpph.archive.web_link,
        bpph.binary_package_name,
        version,
        arch,
        )


def get_package_info_from_publication(bpph):
    arch = bpph.distro_arch_series.architecture_tag
    url = deb_file_url_for_publication(bpph)
    return url, arch


def get_libdep_mapping_for_package(url):
    """Return the library -> dependency mapping for the package at url.

    :return: a dict mapping library names to dependencies, e.g.
            {'libfoo.so.1': 'libfoo1', ...}
    """
    directory = tempfile.mkdtemp()
    try:
        deb_file = download_file(url, directory)
        return libdep_mapping_for_deb(deb_file)
    finally:
        shutil.rmtree(directory)


@contextmanager
def extract_deb_control(binary_package_path):
    """Extract a deb control archive, returning the extracted path.

    This is a context manager, and the tempdir will be cleaned up when closed.
    """
    temp_dir = tempfile.mkdtemp()
    try:
        run_subprocess(['dpkg-deb', '-e', binary_package_path, temp_dir])
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)


@contextmanager
def extract_deb_content(binary_package_path):
    """Extract the files from a .deb package to a tempdir.

    This is a context manager, the path to the tempdir will be yielded
    to the caller, and the tempdir will be cleaned up when closed.
    """
    temp_dir = tempfile.mkdtemp()
    try:
        run_subprocess(['dpkg-deb', '-x', binary_package_path, temp_dir])
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)


def get_file_contents(path):
    """Read the contents of the file at `path`.

    :return: the contents of the file, or None if there was
        no such file.
    :raises: Any errors opening or reading the file.
    """
    try:
        return open(path).read()
    except (OSError, IOError), e:
        if e.errno == errno.ENOENT:
            return
        raise


def libdep_mapping_from_symbols(symbol_contents):
    """Returns a dict mapping libraries to dependencies based on the symbols

    Ignores versions and a whole bunch of other stuff and is probably the
    wrong API even.
    """

    # XXX: This is going to yield sonames and package names for now. Really,
    # there should be something parsing the symbols file and another thing to
    # somehow turn those into dependencies with versions.

    # Doesn't know how to handle lines like this:
    #
    # libformw.so.5 #PACKAGE#.
    #
    # This is OK, as we're only processing symbols files from binary packages
    # rather than source packages.

    mapping = {}
    for line in symbol_contents.splitlines():
        if not line:
            # Blank lines are skipped
            continue
        if line.startswith('|'):
            # Alternative dependency template
            # e.g. | libgl1-mesa-glx #MINVER#
            continue
        if line.startswith('*'):
            # Meta-information
            # e.g. * Build-Depends-Package: libgl1-mesa-dev
            continue
        if line.startswith(' '):
            # Symbol
            # e.g.  gdk_add_client_message_filter@Base 2.8.0
            continue
        if line.startswith('#'):
            # Lines starting with '#' are comments.  There are also DEPRECATED
            # and MISSING, and jml doesn't really know what they mean
            continue
        library, dependency = tuple(line.split()[:2])
        if '#include' in library:
            # To skip lines that are includes.  XXX: Properly ought to process
            # the tags that might appear before the include
            # line.
            #
            # e.g. (arch=!armel)#include "libdiagnostics0.symbols.backtrace"
            continue
        mapping[library] = dependency
    return mapping


def shared_objects_from_shlibs(shlibs_contents):
    """Get the shared object info from the shlibs file.

    http://www.debian.org/doc/debian-policy/ch-sharedlibs.html#s-sharedlibs-shlibdeps
    defines the format.

    :return: a dict mapping (libname, soname) to dependencies.
    """
    mapping = {}
    for line in shlibs_contents.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            continue
        libname, soname, dependency = line.split(' ', 2)
        if libname.endswith(':'):
            # This is a 'type' marker, currently only udeb is used, and
            # we don't want those
            continue
        mapping[(libname, soname)] = dependency
    return mapping


class URI(StormURI):
    """A stand-in for Storm's URI class.

    This class implements the same interface as `storm.uri.URI`, except
    that the constructor has a different signature. Storm's version takes
    a string and parses it, this version can be used when you already
    have a parsed version and just need to create the object.
    """

    def __init__(self, scheme=None, host=None, port=None, username=None,
                 password=None, database=None, options=None):
        self.scheme = scheme
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.options = options
        if self.options is None:
            self.options = dict()


class PackageDatabase(object):

    # the various db backends, aptfile is a bit special
    SQLITE = 'sqlite'
    POSTGRES = 'postgres'
    APTFILE = 'aptfile'

    def __init__(self, store):
        self._store = store

    @classmethod
    def _get_storm_sqlite_connection_uri(cls, opts):
        raise ValueError(
            "SQLite is no longer supported, you must migrate to postgresql.")

    @classmethod
    def _get_storm_postgres_connection_uri(cls, opts):
        if not getattr(opts, 'database_db_name', None):
            raise ValueError(
                "Can't create database, no connection info available. "
                "You must specify %s. Looked in %s. "
                "Perhaps %s is set incorrectly?" % (
                    'db_name', get_config_file_path(), CONF_FILE_ENV_VAR))
        return URI(scheme=opts.database_db_type,
                   username=opts.database_username,
                   password=opts.database_password,
                   host=opts.database_host,
                   port=opts.database_port,
                   database=opts.database_db_name)

    @classmethod
    def _get_storm_connection_uri(cls, opts):
        if opts.database_db_type == cls.POSTGRES:
            return cls._get_storm_postgres_connection_uri(opts)
        elif opts.database_db_type == cls.SQLITE:
            return cls._get_storm_sqlite_connection_uri(opts)
        else:
            raise AssertionError(
                "Unsupported database: %s" % opts.database_db_type)

    @classmethod
    def get_db_info_from_config(cls, opts):
        return cls._get_storm_connection_uri(opts)

    @classmethod
    def get_store_from_config(cls, opts):
        """Create a storm store based on a config file.

        This method will create a storm store based
        on the information in ``~/.config/pkgme-binary/conf``

        :return: a tuple of (store, store_type), where store_type
            is one of cls.SQLITE or cls.POSTGRES, indicating what
            is at the other end of the store.
        """
        connection_info = cls.get_db_info_from_config(opts)
        database = create_database(connection_info)
        return Store(database)

    @classmethod
    def create(cls, store=None):
        if store is None:
            options = load_configuration().options
            # XXX: not elegant
            if options.database_db_type == cls.APTFILE:
                return AptFilePackageDatabase(options.database_aptfile_cachedir)
            store = cls.get_store_from_config(options)
        return cls(store)

    def get_dependencies(self, library_name, arch='i386'):
        """Get the binary packages that provide 'library_name'."""
        result = self._store.execute(
            "SELECT dependency FROM libdep WHERE library = ? AND architecture = ?",
                  (unicode(library_name), unicode(arch)))
        return set([dependency for [dependency] in result])

    def insert_new_library(self, package_name, library_name,
                           dependency, arch):
        """Insert a library and its needed dependency into the database.

        :param library_name: A full soname, e.g. libfoo.so.1.
        :param dependency: A binary package dependency, possibly including
            version.
        """
        self._store.execute(
            "INSERT INTO libdep VALUES (?, ?, ?, ?)",
            (unicode(package_name),
             unicode(library_name),
             unicode(dependency),
             unicode(arch)))

    def update_package(self, package_name, arch_libdep_mapping):
        """Update the database with the libdep info from 'package_name'.

        :param package_name: The name of the package where the
            symbols came from.
        :param arch_libdep_mapping: a dict mapping architecture tags to dicts
            mapping library names to dependencies, e.g.
                {'amd64': {'libfoo.so.1': 'libfoo1', ...}, ...}
        """
        for arch, libdep_mapping in arch_libdep_mapping.items():
            self._store.execute(
                    "DELETE FROM libdep WHERE source_package_name = ? "
                    "AND architecture = ?",
                    (unicode(package_name), unicode(arch)))
            for library, dependency in libdep_mapping.items():
                self.insert_new_library(
                    package_name, library, dependency, arch)
        self._store.commit()

    def close(self):
        self._store.close()


def dict_add(*dicts):
    """Add dicts, with later dicts taking precedence."""
    result = dict()
    for d in dicts:
        result.update(d)
    return result


def publishings_to_package_info(publishings):
    """Takes a list of publishings and returns the info for the library packages.

    :param publishings: an iterable of launchpadlib
        binary_package_publishing_history objects.
    :return: an iterable of (.deb url, arch tag) for the publishings
        that represent a library package.
    """
    packages_info = map(get_package_info_from_publication, publishings)
    return filter(
            lambda (url, arch): is_library_package(url),
            packages_info)


def fetch_symbol_files(scan_mode, package_name, db):
    """Insert the libdep info for ``package_name`` into ``db``."""
    if scan_mode != 'binary':
        raise AssertionError("Unsupported scan mode: {0}".format(scan_mode))
    with LaunchpadFixture(APPLICATION_NAME, SERVICE_ROOT) as lp:
        publishings = iter_published_binaries(lp.anonymous, name=package_name)
        lib_packages_info = publishings_to_package_info(publishings)
        def arch_libdep_for_package((url, arch)):
            return {arch: get_libdep_mapping_for_package(url)}
        arch_libdep_mapping = dict_add(
                *map(arch_libdep_for_package, lib_packages_info))
    db.update_package(package_name, arch_libdep_mapping)


def main():
    """Import the symbol files for 'package_name'."""
    glue = load_configuration()
    with closing(PackageDatabase.get_store_from_config(glue.options)) as store:
        package_name = glue.args[0]
        db = PackageDatabase(store)
        fetch_symbol_files(glue.options.scan_mode, package_name, db)
