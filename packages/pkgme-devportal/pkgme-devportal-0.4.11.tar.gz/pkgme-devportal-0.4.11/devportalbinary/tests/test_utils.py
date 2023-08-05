# Copyright 2012 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Tests for devportalbinary.utils."""

import os
from StringIO import StringIO
from urllib2 import (
    HTTPError,
    URLError,
    )

import Image

from fixtures import TempDir
from testtools import (
    TestCase,
    ExpectedException,
    )
from testtools.matchers import (
    FileContains,
    MismatchError,
    )
from treeshape import (
    CONTENT,
    FileTree,
    )

from devportalbinary import utils

from devportalbinary.testing import IsImage, IsChildPath


class TestOpenForWriting(TestCase):

    def assertIsWriteable(self, fd, path):
        contents = self.getUniqueString()
        os.write(fd, contents)
        os.close(fd)
        self.assertThat(path, FileContains(contents))

    def test_default(self):
        fd, path = utils._open_file_for_writing('http://example.org/foo')
        self.addCleanup(os.unlink, path)
        self.assertIsWriteable(fd, path)

    def test_directory_provided(self):
        temp_path = self.useFixture(TempDir()).path
        fd, path = utils._open_file_for_writing(
            'http://example.org/foo', temp_path)
        self.assertIsWriteable(fd, path)
        self.assertEqual(os.path.join(temp_path, 'foo'), path)

    def test_name_provided(self):
        fd, path = utils._open_file_for_writing(
            'http://example.org/foo', name='bar')
        self.addCleanup(os.unlink, path)
        self.assertIsWriteable(fd, path)
        self.assertEqual('bar', os.path.basename(path))

    def test_directory_and_name_provided(self):
        temp_path = self.useFixture(TempDir()).path
        fd, path = utils._open_file_for_writing(
            'http://example.org/foo', temp_path, name='bar')
        self.assertIsWriteable(fd, path)
        self.assertEqual(os.path.join(temp_path, 'bar'), path)

    def test_working_directory_no_name(self):
        working_dir = self.useFixture(TempDir()).path
        fd, path = utils._open_file_for_writing(
            'http://example.org/foo', working_dir=working_dir)
        self.assertIsWriteable(fd, path)
        self.assertThat(path, IsChildPath(working_dir))

    def test_working_directory_name(self):
        working_dir = self.useFixture(TempDir()).path
        fd, path = utils._open_file_for_writing(
            'http://example.org/foo', name='bar', working_dir=working_dir)
        self.assertIsWriteable(fd, path)
        self.assertEqual('bar', os.path.basename(path))
        self.assertThat(path, IsChildPath(working_dir))


class TestDownloadFile(TestCase):

    def test_saves_file(self):
        contents = self.getUniqueString()
        def urlopen(url):
            return StringIO(contents)
        self.patch(utils, 'urlopen', urlopen)
        path = utils.download_file('http://example.org/foo')
        self.assertThat(path, FileContains(contents))

    def test_url_error_includes_url(self):
        def urlopen(url):
            raise URLError("whatever")
        self.patch(utils, 'urlopen', urlopen)
        url = 'http://example.org/foo'
        e = self.assertRaises(URLError, utils.download_file, url)
        self.assertEqual("<urlopen error whatever: %s>" % (url,), str(e))

    def test_http_error_includes_url(self):
        url = 'http://example.org/foo'
        # HTTPError must get a valid fp, otherwise it won't store the URL.
        tree = self.useFixture(FileTree({'thing.txt': {CONTENT: 'whatever'}}))
        fp = open(os.path.join(tree.path, 'thing.txt'), 'r')
        def urlopen(url):
            raise HTTPError(url, 404, 'whatever dude', {}, fp)
        self.patch(utils, 'urlopen', urlopen)
        e = self.assertRaises(HTTPError, utils.download_file, url)
        self.assertEqual(
            "HTTP Error 404: whatever dude: <%s>" % (url,), str(e))


class IsImageTestCase(TestCase):

    def setUp(self):
        super(IsImageTestCase, self).setUp()
        self.tempdir = self.useFixture(TempDir()).path
        self.img_path = os.path.join(self.tempdir, "foo.png")
        img = Image.new("RGB", (48,48), "black")
        img.save(self.img_path)

    def test_is_right_image(self):
        self.assertThat(self.img_path, IsImage())
        self.assertThat(self.img_path, IsImage(kind="png"))
        self.assertThat(self.img_path, IsImage(width=48, kind="png"))
        self.assertThat(self.img_path, IsImage(width=48, height=48, kind="png"))

    def test_is_not_quite_the_right_image(self):
        with ExpectedException(MismatchError):
            self.assertThat(self.img_path, IsImage(width=900, kind="png"))
        with ExpectedException(MismatchError):
            self.assertThat(self.img_path, IsImage(kind="xpm"))
        with ExpectedException(MismatchError):
            no_img = os.path.join(self.tempdir, "bar.png")
            with open(no_img, "w") as fp:
                fp.write("I'm not a image")
            self.assertThat(no_img, IsImage())


class TestFirstPathComponent(TestCase):

    def test_filename(self):
        filename = self.getUniqueString()
        self.assertEqual(filename, utils.first_path_component(filename))

    def test_directory(self):
        filename = self.getUniqueString()
        directory = self.getUniqueString()
        self.assertEqual(directory,
                utils.first_path_component(os.path.join(directory, filename)))

    def test_subdir(self):
        filename = self.getUniqueString()
        directory = self.getUniqueString()
        subdir = self.getUniqueString()
        self.assertEqual(directory,
                utils.first_path_component(
                    os.path.join(directory, subdir, filename)))

    def test_absolute(self):
        filename = self.getUniqueString()
        directory = self.getUniqueString()
        self.assertEqual(directory,
                utils.first_path_component(
                    '/' + os.path.join(directory, filename)))

    def test_empty(self):
        self.assertEqual('', utils.first_path_component(''))
