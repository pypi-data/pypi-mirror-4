# Copyright 2012 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

__all__ = [
    'AptFilePackageDatabase',
    ]

import gzip
import urllib
import argparse
import os
import re


def make_arg_parser():
    p = argparse.ArgumentParser()
    p.add_argument('--cache-dir', type=str, default='cache')
    p.add_argument('output_file', type=argparse.FileType('w'))
    return p


so_filename_re = re.compile(r'\.so(\.[0-9]+)*$')
def export_database(db, stream):
    for library, package, arch in db.iter_database():
        if so_filename_re.search(library):
            stream.write(','.join([package, library, package, arch]))
            stream.write('\n')
            stream.flush()


def dump_apt_file_db():
    parser = make_arg_parser()
    args = parser.parse_args()
    if not os.path.isdir(args.cache_dir):
        os.path.makedirs(args.cache_dir)
    db = AptFilePackageDatabase(args.cache_dir)
    export_database(db, args.output_file)
    return 0


def iter_contents_file(contents):
    """ Yield (full-library-path, set-of-pkgnames) from a Contents file.

    It expects a line starting with "FILE" that tells it when the header ends
    and the actual content starts.
    """
    found_start_marker = False
    for line in contents:
        if not found_start_marker:
            if line.startswith("FILE"):
                found_start_marker = True
            continue
        (path, sep, pkgs) = [s.strip() for s in line.rpartition(" ")]
        # pkgs is formated a bit funny, e.g. universe/pkgname
        pkgs = set([os.path.basename(pkg) for pkg in pkgs.split(",")])
        yield (path, pkgs)


class AptFilePackageDatabase(object):
    """Really dumb database that just uses apt-file for local testing """

    # we could also read /etc/ld.so.conf.d/*.conf but this maybe different on
    # different distroseries especially if
    #    server-distroseries != target-distroseries
    #  (I wish there was ldconfig --print-search-dirs)
    LD_SEARCH_PATH = [
        # standards
        "lib",
        "usr/lib",
        "usr/local/lib",
        # old biarch
        "lib32",
        "usr/lib32",
        # new multiarch
        "lib/i686-linux-gnu",
        "lib/i386-linux-gnu",
        "lib/x86_64-linux-gnu",
        "usr/lib/i386-linux-gnu",
        "usr/lib/i686-linux-gnu",
        "usr/lib/x86_64-linux-gnu",
        # ?
        "usr/lib/x86_64-linux-gnu/fakechroot",
        "usr/lib/x86_64-linux-gnu/mesa",
        "usr/lib/x86_64-linux-gnu/mesa-egl",
        "usr/lib/i386-linux-gnu/mesa",
        ]

    DISTROSERIES = "oneiric"

    # If db_type is set to this in the config, that means use this database.
    DB_TYPE =  'aptfile'

    CONTENTS_FILE_URL_LOCATION = (
        "http://archive.ubuntu.com/ubuntu/dists/%(distroseries)s/"
        "Contents-%(arch)s.gz")

    CONTENTS_FILE = "Contents-%(distroseries)s-%(arch)s"

    def __init__(self, cachedir):
        self.cachedir = os.path.expanduser(cachedir)
        self._distroseries_arch_cache = {}

    @classmethod
    def from_options(cls, options):
        return cls(options.database_aptfile_cachedir)

    def _get_lib_to_pkgs_mapping(self, distroseries, arch):
        """Returns a dict of { library-name : set([pkg1,pkg2])

        This function will return a dict to lookup library-name to package
        dependencies for the given distroseries and architecture
        """
        if not (distroseries, arch) in self._distroseries_arch_cache:
            self._distroseries_arch_cache[(distroseries, arch)] = \
                      self._get_mapping_from_contents_file(distroseries, arch)
        return self._distroseries_arch_cache[(distroseries, arch)]

    def _get_contents_file_cache_path(self, distroseries, arch):
        """Return the path in the cache for the given distroseries, arch """
        return os.path.join(
            self.cachedir, self.CONTENTS_FILE % {
                'distroseries': distroseries, 'arch': arch})

    def _get_contents_file_server_url(self, distroseries, arch):
        """Return the remote server URL for the given distroseries, arch """
        return self.CONTENTS_FILE_URL_LOCATION % {
            'distroseries': distroseries, 'arch': arch}

    def _get_mapping_from_contents_file(self, distroseries, arch):
        """Return lib,pkgs mapping from contents file for distroseries, arch

        This expects the contents file to be in the cachedir already.
        """
        lib_to_pkgs = {}
        path = self._get_contents_file_cache_path(distroseries, arch)
        with open(path) as f:
            for path, pkgs in self._iter_contents_file(f):
                basename = os.path.basename(path)
                if not basename in lib_to_pkgs:
                    lib_to_pkgs[basename] = set()
                lib_to_pkgs[basename] |= pkgs
        return lib_to_pkgs

    def _download_contents_file_compressed(self, distroseries, arch):
        """Downloads the content file for distroseries, arch into target """
        # XXX: we may eventually want to merge the Contents files from
        #      the -updates repository too in addition to the main archive
        url = self._get_contents_file_server_url(distroseries, arch)
        target = self._get_contents_file_cache_path(distroseries, arch)
        compressed_target = target + os.path.splitext(url)[1]
        # download
        urllib.urlretrieve(url, compressed_target)
        return compressed_target

    def _iter_contents_file(self, in_file):
        for path, pkgs in iter_contents_file(in_file):
            if os.path.dirname(path) in self.LD_SEARCH_PATH:
                yield path, pkgs

    def _prune_contents_gz_file(self, infile, outfile):
        """Read a compressed Contents.gz and write out a pruned version.

        This will use iter_contents_file to go over infile and write
        the relevant lines that are in the LD_SEARCH_PATH to outfile.
        """
        with open(outfile, "w") as outf, gzip.open(infile) as inf:
            # first write the header
            outf.write("FILE  LOCATION\n")
            # then iter over all relevant lines and write them out
            for path, pkgs in self._iter_contents_file(inf):
                outf.write("%s %s\n" % (path, ",".join(pkgs)))

    def _download_and_prepare_contents_file_if_needed(self, distroseries, arch):
        """Ensure there is a usable Contents file in the cachedir

        This will download, uncompress and prune a Conents file for
        distroseries, arch so that get_dependencies works.
        """
        # mvo: We can (and should eventually) do etag/if-modified-since
        #      matching here. But its not really important as long as
        #      we package for stable distroseries as the Contents file
        #      will not change
        path = self._get_contents_file_cache_path(distroseries, arch)
        if not os.path.exists(path):
            compressed_contents = self._download_contents_file_compressed(
                distroseries, arch)
            # and prune from ~300mb to 1mb uncompressed as we are only
            # interested in the library path parts
            self._prune_contents_gz_file(compressed_contents, path)
            os.remove(compressed_contents)

    def iter_database(self, architectures=('i386', 'amd64'),
                      distroseries=None):
        """Export the database.

        Yields (library, package, arch) tuples for everything that we can
        find.
        """
        # XXX: Untested
        if distroseries is None:
            distroseries = self.DISTROSERIES
        for arch in architectures:
            self._download_and_prepare_contents_file_if_needed(
                distroseries, arch)
            mapping = self._get_lib_to_pkgs_mapping(distroseries, arch)
            for library in mapping:
                for package in mapping[library]:
                    yield library, package, arch

    def get_dependencies(self, lib, arch="i386"):
        # do lazy downloading for now, we could also make this part
        # of bin/fetch-symbols I guess(?)
        self._download_and_prepare_contents_file_if_needed(
            self.DISTROSERIES, arch)
        lib_to_pkgs = self._get_lib_to_pkgs_mapping(self.DISTROSERIES, arch)
        return lib_to_pkgs.get(lib)

    def close(self):
        pass
