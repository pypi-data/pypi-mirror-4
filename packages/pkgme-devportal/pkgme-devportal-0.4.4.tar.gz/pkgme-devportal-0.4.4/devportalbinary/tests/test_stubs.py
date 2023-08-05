# Copyright 2011-2012 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from pkgme.errors import PkgmeError
from testtools import TestCase

from ..metadata import MetadataBackend
from ..stubs import (
    BackendNotImplemented,
    DebianBinaryBackend,
    DebianSourceBackend,
    JarBackend,
    StubBackend,
    PythonBackend,
    TextBackend,
    UnimplementableBackend,
    )
from ..testing import BackendTests


VALID_METADATA_FILE = (MetadataBackend.METADATA_FILE, '{}')


class BackendNotImplementedTests(TestCase):

    def test_str(self):
        e = BackendNotImplemented('backend_name')
        self.assertEqual('backend_name not implemented yet', str(e))

    def test_user_friendly(self):
        e = BackendNotImplemented('backend_name')
        self.assertIsInstance(e, PkgmeError)


class UnimplementableTests(TestCase):

    def test_str(self):
        e = UnimplementableBackend('backend_name')
        self.assertEqual('backend_name will never be implemented', str(e))

    def test_str_with_reason(self):
        e = UnimplementableBackend(
            'backend_name', "You can't package a text file!")
        self.assertEqual(
            ("backend_name will never be implemented: You can't package "
             "a text file!"),
            str(e))

    def test_user_friendly(self):
        e = UnimplementableBackend('backend_name')
        self.assertIsInstance(e, PkgmeError)


class StubTests(BackendTests):

    BACKEND = StubBackend

    def test_get_info(self):
        backend = self.make_backend()
        self.assertRaises(BackendNotImplemented, backend.get_info)


class JavaTests(BackendTests):

    BACKEND = JarBackend

    def test_want_with_only_metadata(self):
        self.assertEqual(
            {'score': 0, 'reason': 'No files found, just metadata'},
            self.want([VALID_METADATA_FILE]))

    def test_want_with_only_jar(self):
        filename = self.getUniqueString() + '.jar'
        self.assertEqual(
            {'score': 5, 'reason': None},
            self.want([VALID_METADATA_FILE, filename]))

    def test_want_with_only_non_jars(self):
        filename = self.getUniqueString() + '.txt'
        self.assertEqual(
            {'score': 0, 'reason': "No .jars found: %r" % ([filename],)},
            self.want([VALID_METADATA_FILE, filename]))


class DebianSourceTests(BackendTests):

    BACKEND = DebianSourceBackend

    def test_want_with_only_metadata(self):
        self.assertEqual(
            {'score': 0, 'reason': 'No files found, just metadata'},
            self.want([VALID_METADATA_FILE]))

    def test_want_with_random_files(self):
        filename = self.getUniqueString() + '.txt'
        self.assertEqual(
            {'score': 0, 'reason': "No .dsc found: %r" % ([filename],)},
            self.want([VALID_METADATA_FILE, filename]))

    def test_want_with_dsc(self):
        filename = self.getUniqueString() + '.dsc'
        self.assertEqual(
            {'score': 5, 'reason': None},
            self.want([VALID_METADATA_FILE, filename]))


class DebianBinaryTests(BackendTests):

    BACKEND = DebianBinaryBackend

    def test_want_with_only_metadata(self):
        self.assertEqual(
            {'score': 0, 'reason': 'No files found, just metadata'},
            self.want([VALID_METADATA_FILE]))

    def test_want_with_random_files(self):
        filename = self.getUniqueString() + '.txt'
        self.assertEqual(
            {'score': 0, 'reason': "No .debs found: %r" % ([filename],)},
            self.want([VALID_METADATA_FILE, filename]))

    def test_want_with_dsc(self):
        filename = self.getUniqueString() + '.deb'
        self.assertEqual(
            {'score': 5, 'reason': None},
            self.want([VALID_METADATA_FILE, filename]))


class TextTests(BackendTests):

    BACKEND = TextBackend

    def test_want_with_only_metadata(self):
        self.assertEqual(
            {'score': 0, 'reason': 'No files found, just metadata'},
            self.want([VALID_METADATA_FILE]))

    def test_want_with_random_files(self):
        filename = self.getUniqueString() + '.data'
        self.assertEqual(
            {'score': 0, 'reason': "File is not a .txt: %r" % (filename,)},
            self.want([VALID_METADATA_FILE, filename]))

    def test_want_with_only_txt(self):
        filename = self.getUniqueString() + '.txt'
        self.assertEqual(
            {'score': 20, 'reason': None},
            self.want([VALID_METADATA_FILE, filename]))

    def test_want_with_more_than_txt(self):
        txt_file = self.getUniqueString() + '.txt'
        other_file = self.getUniqueString() + '.exe'
        self.assertEqual(
            {'score': 0,
             'reason': ('More files than just a .txt: %r' %
                        (sorted([txt_file, other_file]),))},
            self.want([VALID_METADATA_FILE, txt_file, other_file]))

    def test_get_info(self):
        backend = self.make_backend()
        self.assertRaises(UnimplementableBackend, backend.get_info)


class PythonTests(BackendTests):

    BACKEND = PythonBackend

    def test_want_with_only_metadata(self):
        self.assertEqual(
            {'score': 0, 'reason': 'No files found, just metadata'},
            self.want([VALID_METADATA_FILE]))

    def test_want_with_random_files(self):
        filename = self.getUniqueString() + '.data'
        self.assertEqual(
            {'score': 0, 'reason': "No setup.py found"},
            self.want([VALID_METADATA_FILE, filename]))

    def test_want_with_only_setup_py(self):
        self.assertEqual(
            {'score': 0, 'reason': "setup.py found, but nothing else"},
            self.want([VALID_METADATA_FILE, 'setup.py']))

    def test_want_with_more_than_setup_py(self):
        other_file = self.getUniqueString()
        self.assertEqual(
            {'score': 5, 'reason': None},
            self.want([VALID_METADATA_FILE, "setup.py", other_file]))

    def test_get_info(self):
        backend = self.make_backend()
        self.assertRaises(BackendNotImplemented, backend.get_info)
