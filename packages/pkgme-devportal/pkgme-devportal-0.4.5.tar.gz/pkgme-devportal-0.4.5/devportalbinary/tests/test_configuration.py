# Copyright 2011-2012 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import os

from fixtures import (
    EnvironmentVariableFixture,
    TempDir,
    )
from testtools import TestCase

from devportalbinary.configuration import (
    _DEFAULT_CONF_FILE,
    CONF_FILE_ENV_VAR,
    get_config_file_path,
    load_configuration,
    )
from devportalbinary.testing import make_config_section


class TestConfigFileLocation(TestCase):

    def test_default(self):
        self.assertEqual(
            os.path.expanduser(_DEFAULT_CONF_FILE), get_config_file_path())

    def test_env_var_override(self):
        tempdir = self.useFixture(TempDir())
        config_file = os.path.join(tempdir.path, 'whatever.ini')
        self.useFixture(
            EnvironmentVariableFixture(CONF_FILE_ENV_VAR, config_file))
        self.assertEqual(config_file, get_config_file_path())

    def test_load_configuration(self):
        # load_configuration reads from the configuration file returned by
        # get_config_file_path.
        tempdir = self.useFixture(TempDir())
        config_file = os.path.join(tempdir.path, 'whatever.ini')
        self.useFixture(
            EnvironmentVariableFixture(CONF_FILE_ENV_VAR, config_file))
        db_name = self.getUniqueString()
        with open(config_file, 'w') as f:
            f.write(make_config_section(
                'database',
                {'db_type': 'postgres', 'db_name': db_name}))
            f.write('\n')
        config = load_configuration()
        self.assertEqual(
            ('postgres', db_name),
            (config.options.database_db_type, config.options.database_db_name))
