# Copyright 2011 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from unittest import TestLoader

from testresources import OptimisingTestSuite


def test_suite():
    """Insert an OptimizingTestSuite for testresources."""
    module_names = [
        'devportalbinary.tests.test_backend',
        'devportalbinary.tests.test_binary',
        'devportalbinary.tests.test_configuration',
        'devportalbinary.tests.test_database',
        'devportalbinary.tests.test_metadata',
        'devportalbinary.tests.test_pdf',
        'devportalbinary.tests.test_stubs',
        'devportalbinary.tests.test_unity_webapps',
        'devportalbinary.tests.test_utils',
        ]
    loader = TestLoader()
    tests = OptimisingTestSuite()
    tests.addTests(loader.loadTestsFromNames(module_names))
    return tests
