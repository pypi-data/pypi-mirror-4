# Copyright 2011-2012 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import os

from devportalbinary.metadata import (
    get_excluded_package_files,
    get_package_files,
    make_all_info_fn,
    make_want_fn,
    MetadataBackend,
    )


class PdfBackend(MetadataBackend):
    """A backend that uses MyApps metadata to build a package for a PDF."""

    def get_architecture(self):
        return 'all'

    def get_build_depends(self):
        return 'debhelper (>=7)'

    def get_explicit_copyright(self):
        # See https://bugs.launchpad.net/pkgme-devportal/+bug/1026121/.
        maintainer = self.get_maintainer()
        if maintainer:
            maintainer_suffix = (
                " or contact the submitter of the PDF, %s" % (maintainer,))
        else:
            maintainer_suffix = ''
        return """\
Please see the enclosed PDF file for the exact copyright holders%s.

This file was automatically generated.
""" % (maintainer_suffix,)

    def get_depends(self):
        return 'xdg-utils, ${misc:Depends}'

    def get_executable(self, package_name):
        pdf_filename = None
        for filename in os.listdir(self.path):
            if filename.endswith('.pdf'):
                pdf_filename = filename
                break
        if pdf_filename is None:
            return None
        return '/usr/bin/xdg-open /opt/%s/%s' % (package_name, pdf_filename)

    @classmethod
    def want_with_metadata(cls, path, metadata):
        excluded_files = get_excluded_package_files(cls, metadata)
        files = list(get_package_files(path, excluded_files))
        # By default, we don't want it and give no reason.  Sane default in
        # case of buggy code below.
        score = 0
        reason = None
        if len(files) == 0:
            reason = 'No files found, just metadata'
        elif len(files) == 1:
            filename = files[0]
            if filename.endswith(".pdf"):
                score = 20
            else:
                reason = 'File is not a PDF: %r' % (filename,)
        else:
            reason = 'More files than just a PDF: %r' % (sorted(files),)
        return {'score': score, 'reason': reason}


want = make_want_fn(PdfBackend)
all_info = make_all_info_fn(PdfBackend)
