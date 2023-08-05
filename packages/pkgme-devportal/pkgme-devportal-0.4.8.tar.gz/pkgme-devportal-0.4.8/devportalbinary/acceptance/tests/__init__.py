import os
import shutil
import subprocess

from fixtures import Fixture, MonkeyPatch, TempDir
from testtools import TestCase
from testtools.matchers import Contains
from treeshape import (
    CONTENT,
    HasFileTree,
    )

import pkgme
from pkgme.backend import NoEligibleBackend
from pkgme.debuild import build_source_package
from pkgme.run_script import ScriptUserError

from devportalbinary.testing import DatabaseFixture, IsImage


class TestData(Fixture):

    def __init__(self, datadir):
        self.datadir = datadir

    def setUp(self):
        Fixture.setUp(self)
        tempdir = self.useFixture(TempDir())
        self.path = os.path.join(tempdir.path, "target")
        source_path = os.path.join(
            os.path.dirname(__file__), "..", "data", self.datadir)
        shutil.copytree(source_path, self.path)


BACKEND_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "devportalbinary", "backends")


def get_allowed_backends():
    return os.listdir(BACKEND_DIR)


def run_pkgme(test_data):
    patch = MonkeyPatch("pkgme.backend.EXTERNAL_BACKEND_PATHS", [BACKEND_DIR])
    with patch:
        pkgme.write_packaging(
            test_data.path, allowed_backend_names=get_allowed_backends())
        # also try to build the package to catch any errors there
        build_source_package(test_data.path, sign=False)


def build_binary_package(path):
    proc = subprocess.Popen(["debuild", "-uc", "-us"], cwd=path,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, err = proc.communicate()
    if proc.returncode != 0:
        raise AssertionError(
                "Building binary package from %s failed: %s" % (path, out))


class AcceptanceTests(TestCase):

    def assertErrorsOutWith(self, test_data, error_message):
        e = self.assertRaises(ScriptUserError, run_pkgme, test_data)
        self.assertEqual(error_message, str(e).rstrip())

    def test_empty(self):
        """Should fail for a project with no binaries."""
        test_data = self.useFixture(TestData("empty"))
        self.assertRaises(NoEligibleBackend, run_pkgme, test_data)

    def test_python(self):
        """Should fail for a Python project."""
        test_data = self.useFixture(TestData("python"))
        self.assertErrorsOutWith(test_data, "Python not implemented yet")

    def test_gtk(self):
        """Runs successfully for a basic GTK+ application."""
        dep_db = self.useFixture(DatabaseFixture())
        dep_db.db.update_package("pthreads",
                {'i386': {"libpthread.so.0": "libpthread0"}})
        dep_db.db.update_package("eglibc",
                {'i386': {"libc.so.6": "libc6"}})
        test_data = self.useFixture(TestData("gtk"))
        run_pkgme(test_data)
        self.assertThat(test_data.path, HasFileTree({'debian/control': {}}))

    def test_bundled_library(self):
        """Runs successfully for a basic bundled libary."""
        dep_db = self.useFixture(DatabaseFixture())
        dep_db.db.update_package("eglibc",
                {'i386': {"libc.so.6": "libc6"}})
        test_data = self.useFixture(TestData("bundled_lib"))
        run_pkgme(test_data)
        self.assertThat(
            test_data.path,
            HasFileTree(
                {'debian/control': {},
                 'debian/rules': {
                        CONTENT: Contains("\noverride_dh_shlibdeps:\n\t")},
                 }))

    def test_pdf(self):
        test_data = self.useFixture(TestData("pdf"))
        run_pkgme(test_data)
        self.assertThat(test_data.path, HasFileTree({'debian/control': {}}))

    def test_pdf_with_icons(self):
        test_data = self.useFixture(TestData("pdf_with_icons"))
        run_pkgme(test_data)
        self.assertThat(
            test_data.path,
            HasFileTree(
                {'debian/control': {},
                 'debian/icons/48x48/jabberwocky.png': {},
                 }))

    def test_pdf_with_icons_wrong_size(self):
        test_data = self.useFixture(TestData("pdf_with_icons_wrong_size"))
        run_pkgme(test_data)
        icon_path = 'debian/icons/48x48/jabberwocky.png'
        self.assertThat(
            test_data.path,
            HasFileTree(
                {'debian/control': {},
                 icon_path: {},
                 }))
        generated_icon = os.path.join(test_data.path, icon_path)
        self.assertThat(
            generated_icon, IsImage(width=48, height=48, kind="png"))

    def test_unity_webapp(self):
        test_data = self.useFixture(TestData("unity-webapp"))
        run_pkgme(test_data)
        self.assertThat(test_data.path, HasFileTree({'debian/control': {}}))

    def test_deb_bin(self):
        test_data = self.useFixture(TestData("debian-binary"))
        self.assertErrorsOutWith(
            test_data, "Debian binary not implemented yet")

    def test_deb_src(self):
        test_data = self.useFixture(TestData("debian-src"))
        self.assertErrorsOutWith(
            test_data, "Debian source not implemented yet")

    def test_jar(self):
        test_data = self.useFixture(TestData("jar"))
        self.assertErrorsOutWith(
            test_data, "Java binary not implemented yet")

    def test_text(self):
        test_data = self.useFixture(TestData("text"))
        self.assertErrorsOutWith(
            test_data,
            "Text will never be implemented: You can't package a text file")

    def test_package_name_with_spaces(self):
        test_data = self.useFixture(TestData("package_name_with_spaces"))
        run_pkgme(test_data)
        # Build the binary package, as that's usually where errors with
        # spaces in paths show up.
        build_binary_package(test_data.path)
        self.assertThat(test_data.path, HasFileTree({'debian/control': {}}))


def test_suite():
    import unittest
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(__name__)
    return suite
