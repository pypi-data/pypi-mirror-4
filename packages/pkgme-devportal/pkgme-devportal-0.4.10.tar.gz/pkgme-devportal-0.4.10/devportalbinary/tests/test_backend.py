# Copyright 2011-2012 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import json
import os
from StringIO import StringIO

from fixtures import MonkeyPatch
from pkgme.info_elements import PackageName
from testtools import TestCase

from devportalbinary.backend import (
    backend_script,
    BASE_USER_ERROR,
    convert_info,
    USER_ERROR_RETURN_CODE,
    )


class DummyBackend(object):

    def __init__(self, want, metadata):
        self._want = want
        self._metadata = metadata

    def get_metadata(self):
        return self._metadata

    def get_info(self, path):
        return {PackageName.name: self._metadata}

    def want(self):
        return self._want


class BrokenBackend(object):

    def __init__(self, error, *args, **kwargs):
        self._error = error
        self._args = args
        self._kwargs = kwargs

    def _raise(self):
        raise self._error(*self._args, **self._kwargs)

    def get_metadata(self):
        return {}

    def get_info(self, path):
        raise self._raise()

    def want(self):
        raise self._raise()


class TestConvertInfo(TestCase):

    def test_convert(self):
        package_name = self.getUniqueString()
        info = {PackageName: package_name}
        self.assertEqual(
            {PackageName.name: package_name}, convert_info(info))


class TestBackendScript(TestCase):

    def test_backend_script(self):
        metadata = {'foo': 'bar'}
        backend = DummyBackend(None, metadata)
        output = StringIO()
        backend_script(backend.get_info)(os.getcwd(), output)
        self.assertEqual(
            {PackageName.name: metadata}, json.loads(output.getvalue()))

    def test_default_to_stdout(self):
        stream = StringIO()
        self.useFixture(MonkeyPatch('sys.stdout', stream))
        metadata = {'foo': 'bar'}
        backend = DummyBackend(None, metadata)
        backend_script(backend.get_info)(os.getcwd())
        self.assertEqual(
            {PackageName.name: metadata}, json.loads(stream.getvalue()))

    def test_return_zero_on_success(self):
        metadata = {'foo': 'bar'}
        backend = DummyBackend(None, metadata)
        output = StringIO()
        result = backend_script(backend.get_info)(os.getcwd(), output)
        self.assertEqual(0, result)

    def test_normal_error_raises(self):
        output = StringIO()
        backend = BrokenBackend(RuntimeError, "Told you so")
        self.assertRaises(RuntimeError, backend_script(backend.get_info),
                os.getcwd(), output)

    def test_user_error_logs(self):
        output = StringIO()
        error = StringIO()
        backend = BrokenBackend(BASE_USER_ERROR, "Told you so")
        result = backend_script(backend.get_info)(os.getcwd(), output, error)
        self.assertEqual(USER_ERROR_RETURN_CODE, result)
        self.assertEqual('', output.getvalue())
        self.assertEqual("Told you so\n", error.getvalue())

    def test_passes_path(self):
        output = StringIO()
        expected_path = self.getUniqueString()
        def return_path(path):
            return path
        result = backend_script(return_path)(expected_path, output)
        self.assertEqual(expected_path, json.loads(output.getvalue()))
