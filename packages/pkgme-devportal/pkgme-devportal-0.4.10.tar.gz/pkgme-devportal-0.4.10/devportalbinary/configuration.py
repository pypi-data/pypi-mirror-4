# Copyright 2011-2012 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import os

from configglue import glue
from configglue import parser

from configglue.schema import (
    Schema,
    Section,
    DictOption,
    IntOption,
    StringOption,
    TupleOption,
    )


# The environment variable that controls the config file location.
CONF_FILE_ENV_VAR = 'PKGME_DEVPORTAL_CONFIG_FILE'

# Where to look if the environment variable isn't set.
# XXX: 'pkgme-binary' is the historic name of this package.  Change this
# to look first in ~/.config/pkgme-devportal/conf and then fall back to
# this one.  Once production systems are updated to the new config, remove
# the fallback.
_DEFAULT_CONF_FILE = '~/.config/pkgme-binary/conf'


class DevportalSchema(Schema):

    # database
    database = Section()
    database.db_type = StringOption(default='aptfile',
            help=('The database to use, "postgres", "aptfile" are supported '
                  'values.'))
    database.host = StringOption(default=None,
            help='The database host (for postgres)')
    database.port = IntOption(default=None,
            help='The database port (for postgres)')
    database.username = StringOption(default=None,
            help='The database username (for postgres)')
    database.password = StringOption(default=None,
            help='The database password (for postgres)')
    database.db_name = StringOption(default=None,
            help='The database name (for postgres)')
    database.aptfile_cachedir = StringOption(default="~/.cache/pkgme-devportal",
            help='The cache directory for the aptfile backend')
    database.base_url = StringOption(
        default='https://libdep-service.ubuntu.com/',
        help='The base URL for libdep-service')

    scan_mode = StringOption(
        help='Deprecated option, only binary is supported..',
        default='binary')

    # overrides
    libraries = Section()
    default_lib_overrides = { 'libasound.so.2': 'libasound2',
                              'libGL.so.1': 'libgl1-mesa-glx',
                            }
    libraries.overrides = DictOption(
        default=default_lib_overrides,
        help='mapping of library name to pkgname to force picking selected '
             'dependencies')

    # The architectures that we fetch binary packages for, add symbols
    # to the database and support creating debian packages for.
    architectures = Section()
    architectures.supported = TupleOption(
        # XXX: mvo: it seems we don't need "all" here as we are interessted
        #           in binary symbols only?
        default=("i386", "amd64"),
        help='The architectures that we look at for adding libraries to '
             'our database and that we can build packages for')


def get_config_file_path():
    """Return the path to the configuration file."""
    from_env = os.environ.get(CONF_FILE_ENV_VAR, None)
    if from_env:
        return from_env
    return os.path.expanduser(_DEFAULT_CONF_FILE)


class Options(object):

    def set(self, name, value):
        setattr(self, name, value)


def load_configuration():
    config_location = get_config_file_path()
    config_files = []
    if os.path.exists(config_location):
        config_files.append(config_location)
    schema_parser = parser.SchemaConfigParser(DevportalSchema())
    # tell the SchemaConfigParser that we need our data case-sensitive
    schema_parser.optionxform = str
    schema_parser.read(config_files)
    result = Options()
    for section, data in schema_parser.values().items():
        for option, value in data.items():
            result.set('{}_{}'.format(section, option), value)
    return result


def load_configuration_with_command_line():
    config_location = get_config_file_path()
    config_files = []
    if os.path.exists(config_location):
        config_files.append(config_location)
    # tell the SchemaConfigParser that we need our data case-sensitive
    parser.SchemaConfigParser.optionxform = str
    return glue.configglue(DevportalSchema, config_files)
