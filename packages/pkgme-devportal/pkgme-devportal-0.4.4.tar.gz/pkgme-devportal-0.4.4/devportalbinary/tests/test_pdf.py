# Copyright 2011-2012 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import json
import os

from treeshape import (
    FileTree,
    from_rough_spec,
    )

from devportalbinary.binary import MetadataBackend
from devportalbinary.pdf import PdfBackend
from devportalbinary.testing import BackendTests


VALID_METADATA_FILE = (MetadataBackend.METADATA_FILE, '{}')


class PdfBackendTests(BackendTests):

    BACKEND = PdfBackend

    def make_tree(self, rough_shape):
        return self.useFixture(FileTree(from_rough_spec(rough_shape))).path

    def test_want_with_metadata(self):
        # If we detect the metadata file and a pdf, then we score 20.
        filename = self.getUniqueString() + ".pdf"
        path = self.make_tree([VALID_METADATA_FILE, filename])
        self.assertEqual({'score': 20, 'reason': None}, PdfBackend.want(path))

    def test_want_with_single_non_pdf(self):
        # If we detect a metadata file and a single other file that's not a
        # PDF, we score 0.
        filename = self.getUniqueString() + ".not-pdf"
        path = self.make_tree([VALID_METADATA_FILE, filename])
        self.assertEqual(
            {'score': 0,
             'reason': 'File is not a PDF: %r' % (filename,),
             }, PdfBackend.want(path))

    def test_want_with_just_metadata(self):
        # If we detect just the metadata file then we score 0.
        path = self.make_tree([VALID_METADATA_FILE])
        self.assertEqual(
            {'score': 0, 'reason': 'No files found, just metadata'},
            PdfBackend.want(path))

    def test_want_with_extra_files(self):
        # If we detect other files then we score 0. This is so that
        # this backend doesn't trigger on something that just happens
        # to contain a pdf.
        filename = self.getUniqueString() + ".pdf"
        other_filename = self.getUniqueString() + ".foo"
        path = self.make_tree([VALID_METADATA_FILE, filename, other_filename])
        self.assertEqual(
            {'score': 0, 'reason': 'More files than just a PDF: %r' %
             (sorted([filename, other_filename]),)},
            PdfBackend.want(path))

    def test_want_with_debian_dir(self):
        # If the other file is a debian dir then we score 20 still.
        # This just makes local testing of the backend easier.
        filename = self.getUniqueString() + ".pdf"
        path = self.make_tree([VALID_METADATA_FILE, filename, 'debian/'])
        self.assertEqual({'score': 20, 'reason': None}, PdfBackend.want(path))

    def test_want_with_icons(self):
        icon_file = self.getUniqueString() + '.png'
        metadata = json.dumps({'icons': {'48x48': icon_file}})
        filename = self.getUniqueString() + ".pdf"
        path = self.make_tree([
            (MetadataBackend.METADATA_FILE, metadata), icon_file, filename])
        self.assertEqual({'score': 20, 'reason': None}, PdfBackend.want(path))

    def test_want_with_icons_in_subdir(self):
        # Any subdir that the icons are in is ignored.
        icon_file = os.path.join('icons', self.getUniqueString() + '.png')
        metadata = json.dumps({'icons': {'48x48': icon_file}})
        filename = self.getUniqueString() + ".pdf"
        path = self.make_tree([
            (MetadataBackend.METADATA_FILE, metadata), 'icons/', filename])
        self.assertEqual({'score': 20, 'reason': None}, PdfBackend.want(path))

    def test_architecture(self):
        # The pdf backend set architecture to all
        backend = self.make_backend()
        architecture = backend.get_architecture()
        self.assertEqual('all', architecture)

    def test_build_depends(self):
        # The pdf backend has simple build dependencies
        backend = self.make_backend()
        build_depends = backend.get_build_depends()
        self.assertEqual('debhelper (>=7)', build_depends)

    def test_depends(self):
        # The pdf backend depends on xdg-utils
        backend = self.make_backend()
        depends = backend.get_depends()
        self.assertEqual('xdg-utils, ${misc:Depends}', depends)

    def test_description(self):
        # The pdf backend gets the description from the metadata file.
        expected_description = 'best pdf evar'
        metadata = {MetadataBackend.DESCRIPTION: expected_description}
        backend = self.make_backend(metadata=metadata)
        description = backend.get_description()
        self.assertEqual(expected_description, description)

    def test_executable_opens_pdf(self):
        path = self.make_tree(['foo.pdf'])
        package_name = self.getUniqueString()
        metadata = {PdfBackend.PACKAGE_NAME: package_name}
        backend = PdfBackend(path, metadata)
        executable = backend.get_executable(package_name)
        self.assertEqual(
            '/usr/bin/xdg-open /opt/%s/%s' % (package_name, 'foo.pdf'),
            executable)

    def test_copyright_no_maintainer(self):
        metadata = self.make_metadata()
        backend = self.make_backend(metadata=metadata)
        expected = """\
Please see the enclosed PDF file for the exact copyright holders.

This file was automatically generated.
"""
        self.assertEqual(expected, backend.get_explicit_copyright())

    def test_copyright_with_maintainer(self):
        metadata = self.make_metadata()
        submitter = 'Jonathan Lange <jml@mumak.net>'
        metadata[MetadataBackend.MAINTAINER] = submitter
        backend = self.make_backend(metadata=metadata)
        expected = """\
Please see the enclosed PDF file for the exact copyright holders or contact the submitter of the PDF, Jonathan Lange <jml@mumak.net>.

This file was automatically generated.
"""
        self.assertEqual(expected, backend.get_explicit_copyright())
