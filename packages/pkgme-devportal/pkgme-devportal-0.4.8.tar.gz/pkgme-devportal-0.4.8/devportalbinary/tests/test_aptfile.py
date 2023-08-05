import gzip
import os

from mock import patch
from fixtures import TempDir
from testtools import TestCase

from ..aptfile import AptFilePackageDatabase


class AptFilePackageDatabaseTestCase(TestCase):

    # point to our local contents file version that is a tad smaller
    CONTENTS_CACHE = os.path.join(
        os.path.dirname(__file__), "data", "apt-file-backend")

    def setUp(self):
        super(AptFilePackageDatabaseTestCase, self).setUp()
        self.db = AptFilePackageDatabase(self.CONTENTS_CACHE)

    def test_read_fixture_contents_worked(self):
        """ test that our fixture Contents file works as expected """
        # our test DB has 4 entries in the default search path
        self.assertEqual(
            len(self.db._get_lib_to_pkgs_mapping("oneiric", "i386")), 4)

    def test_get_dependencies(self):
        """ Test that data from the fixture dependencies file works """
        self.assertEqual(
            self.db.get_dependencies("libz.so.1"), set(["zlib1g"]))

    @patch("urllib.urlretrieve")
    def test_lazy_downloading(self, mock_urlretrieve):
        """ test that lazy downloading works """
        def _put_fixture_contents_file_in_place(url, target):
            with gzip.open(target, "w") as f:
                f.write("""
Some header text that is ignored
FILE                 LOCATION
usr/lib/libfoo.so.2  pkgfoo,pkgbar
""")
        tempdir = self.useFixture(TempDir())
        db = AptFilePackageDatabase(tempdir.path)
        mock_urlretrieve.side_effect = _put_fixture_contents_file_in_place
        self.assertEqual(
            db.get_dependencies("libfoo.so.2", arch="i386"),
            set(["pkgfoo", "pkgbar"]))
        self.assertEqual(len(db._get_lib_to_pkgs_mapping("oneiric", "i386")), 1)

    def test_close(self):
        # Test that there is a close method we can call
        self.db.close()
