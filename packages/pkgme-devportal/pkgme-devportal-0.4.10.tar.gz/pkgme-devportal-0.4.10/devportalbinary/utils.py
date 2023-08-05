# Copyright 2011 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Miscellaneous utilities that really belong in their own package."""

import os
import tempfile
from urllib2 import (
    HTTPError,
    Request,
    URLError,
    urlopen,
    )

from bzrlib import urlutils
from launchpadlib.launchpad import Launchpad


def _open_file_for_writing(url, directory=None, name=None, working_dir=None):
    """Open a file for writing.

    If neither 'directory' nor 'name' are specified then make a secure
    tempfile with 'mkstemp'.  If directory is specified, then opens a file in
    that directory, either with 'name' or the trailing segment of the URL.  If
    directory is not specified and name is specified, then opens the file in a
    temporary directory.

    If 'working_dir' is specified, then all temporary files or directories
    will be created inside that directory.
    """
    if directory is None:
        if name is None:
            fd, path = tempfile.mkstemp(dir=working_dir)
        else:
            return _open_file_for_writing(
                url, tempfile.mkdtemp(dir=working_dir), name, working_dir)
    else:
        if name is None:
            name = urlutils.unescape(urlutils.basename(url))
        path = os.path.join(directory, name)
        fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_EXCL)
    return fd, path


def _wrap_urlopen(request):
    """urlopen with better error messages."""
    url = request.get_full_url()
    try:
        return urlopen(request)
    except HTTPError, original:
        raise HTTPError(
            original.url,
            original.code,
            '%s: <%s>' % (original.msg, url),
            original.hdrs,
            original.fp,
            )
    except URLError, original:
        if original.args:
            message = '%s: %s' % (str(original.args[0]), url)
        else:
            message = url
        e = URLError(message)
        e.original = original
        raise e


def download_file(url, directory=None, name=None, working_dir=None,
                  bufsize=4 * 2 ** 10, headers=None):
    """Download 'url' into 'directory'."""
    request = Request(url)
    if headers is not None:
        for h in headers:
            request.add_header(h, headers[h])
    download = _wrap_urlopen(request)
    try:
        fd, path = _open_file_for_writing(url, directory, name, working_dir)
        try:
            while True:
                data = download.read(bufsize)
                if not data:
                    return path
                os.write(fd, data)
        finally:
            os.close(fd)
    finally:
        download.close()


_stable_ubuntu_distroseries = None
def get_latest_stable_ubuntu_distroseries():
    """Return the latest stable ubuntu release codename (e.g. "precise")"""
    global _stable_ubuntu_distroseries
    if _stable_ubuntu_distroseries is None:
        # XXX: mvo wonders if a cachedir here would make sense
        cachedir = None
        launchpad = Launchpad.login_anonymously(
            'pkgme-devportal', 'production', cachedir)
        for distroseries in launchpad.distributions["ubuntu"].series:
            if distroseries.status == 'Current Stable Release':
                _stable_ubuntu_distroseries = distroseries.name
    return _stable_ubuntu_distroseries


def first_path_component(path):
    """Return the first component of `path`.

    If `path` has directory elements before the last element
    the the first will be used. Otherwise just the filename
    will be returned. e.g.

        first_path_component('one/two/three') == 'one'
        first_path_component('three') == 'three'
        first_path_component('/one/two') = 'one'
    """
    parts = filter(bool, path.split(os.sep))
    if not parts:
        return ''
    return parts[0]
