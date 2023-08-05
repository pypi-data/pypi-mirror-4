# Copyright 2012 Canonical Ltd.  This software is licensed under the GNU
# Affero General Public License version 3 (see the file LICENSE).


"""Backends that don't actually work.

These are here so that we can gather better data about what people are
submitting.
"""

__all__ = [
    'BackendNotImplemented',
    ]

import os

from pkgme.errors import PkgmeError

from .metadata import (
    get_excluded_package_files,
    get_package_files,
    make_all_info_fn,
    make_want_fn,
    MetadataBackend,
    want_single_file_by_extension,
    )


class BackendNotImplemented(PkgmeError):
    """Raised by backends that are not implemented yet."""

    def __init__(self, backend_name):
        super(BackendNotImplemented, self).__init__(
            "%s not implemented yet" % (backend_name,))


class UnimplementableBackendError(PkgmeError):
    """Raised by backends we'll never implement."""

    def __init__(self, backend_name, reason=None):
        msg = '%s will never be implemented' % (backend_name,)
        if reason:
            msg = ': '.join([msg, reason])
        super(UnimplementableBackendError, self).__init__(msg)


class StubBackend(MetadataBackend):
    """Backend that doesn't do anything.

    Used for gathering stats about what people are uploading.  The only
    interesting bit is the 'want'.
    """

    name = None

    def get_info(self):
        raise BackendNotImplemented(self.name)

    @classmethod
    def want_script(cls, path=None):
        if not path:
            path = os.getcwd()
        return make_want_fn(cls)(path)

    @classmethod
    def all_info_script(cls, path=None):
        if not path:
            path = os.getcwd()
        return make_all_info_fn(cls)(path)


class UnimplementableBackend(StubBackend):

    reason = None

    def get_info(self):
        raise UnimplementableBackendError(self.name, self.reason)


class JarBackend(StubBackend):

    name = 'Java binary'

    @classmethod
    def want_with_metadata(cls, path, metadata):
        score = 0
        reason = None
        excluded_files = get_excluded_package_files(cls, metadata)
        files = get_package_files(path, excluded_files)
        if len(files) == 0:
            reason = 'No files found, just metadata'
        else:
            jars = [f for f in files if f.endswith('.jar')]
            if not jars:
                reason = 'No .jars found: %r' % (list(files),)
            else:
                score = 5
        return {'reason': reason, 'score': score}


class DebianSourceBackend(StubBackend):

    name = 'Debian source'

    @classmethod
    def want_with_metadata(cls, path, metadata):
        score = 0
        reason = None
        excluded_files = get_excluded_package_files(cls, metadata)
        files = get_package_files(path, excluded_files)
        if len(files) == 0:
            reason = 'No files found, just metadata'
        else:
            dscs = [f for f in files if f.endswith('.dsc')]
            if not dscs:
                reason = 'No .dsc found: %r' % (list(files),)
            else:
                score = 5
        return {'reason': reason, 'score': score}


class DebianBinaryBackend(StubBackend):

    name = 'Debian binary'

    @classmethod
    def want_with_metadata(cls, path, metadata):
        score = 0
        reason = None
        excluded_files = get_excluded_package_files(cls, metadata)
        files = get_package_files(path, excluded_files)
        if len(files) == 0:
            reason = 'No files found, just metadata'
        else:
            dscs = [f for f in files if f.endswith('.deb')]
            if not dscs:
                reason = 'No .debs found: %r' % (list(files),)
            else:
                score = 5
        return {'reason': reason, 'score': score}


class TextBackend(UnimplementableBackend):

    name = 'Text'
    reason = "You can't package a text file"

    @classmethod
    def want_with_metadata(cls, path, metadata):
        return want_single_file_by_extension(
            cls, path, metadata, ['.txt'], "a .txt")


class ImageBackend(UnimplementableBackend):

    name = 'Image'
    reason = "You can't package an image"

    EXTENSIONS = [
        '.bmp',
        '.ico',
        '.jpeg',
        '.jpg',
        '.png',
        '.svg',
        ]

    @classmethod
    def want_with_metadata(cls, path, metadata):
        return want_single_file_by_extension(
            cls, path, metadata, cls.EXTENSIONS, "an image")


class PythonBackend(StubBackend):

    name = 'Python'

    @classmethod
    def want_with_metadata(cls, path, metadata):
        score = 0
        reason = None
        excluded_files = get_excluded_package_files(cls, metadata)
        files = get_package_files(path, excluded_files)
        if len(files) == 0:
            reason = 'No files found, just metadata'
        else:
            if "setup.py" in files:
                if len(files) == 1:
                    reason = "setup.py found, but nothing else"
                else:
                    score = 5
            else:
                reason = "No setup.py found"
        return {'reason': reason, 'score': score}


class ShellScriptBackend(StubBackend):

    name = 'Shell script'

    @classmethod
    def want_with_metadata(cls, path, metadata):
        return want_single_file_by_extension(
            cls, path, metadata, ['.sh'], "a .sh", score=5)


class DesktopBackend(UnimplementableBackend):

    name = 'Desktop file'
    reason = "Can't package a .desktop file"

    @classmethod
    def want_with_metadata(cls, path, metadata):
        return want_single_file_by_extension(
            cls, path, metadata, ['.desktop'], "a desktop file")


class DiffBackend(UnimplementableBackend):

    name = 'Diff'
    reason = "Can't package a .diff"

    @classmethod
    def want_with_metadata(cls, path, metadata):
        return want_single_file_by_extension(
            cls, path, metadata, ['.diff'], "a diff")


class ExeBackend(StubBackend):

    name = 'EXE'

    @classmethod
    def want_with_metadata(cls, path, metadata):
        return want_single_file_by_extension(
            cls, path, metadata, ['.exe'], "a .exe", score=5)
