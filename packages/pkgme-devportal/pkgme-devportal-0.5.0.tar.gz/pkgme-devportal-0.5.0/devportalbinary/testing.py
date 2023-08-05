# Copyright 2011-2012 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import json
import os
import random
import shutil
import string

import Image

from testtools.matchers import (
    Equals,
    Matcher,
    Mismatch,
    )

from fixtures import (
    EnvironmentVariableFixture,
    Fixture,
    TempDir,
    )
from testtools import TestCase
from treeshape import (
    from_rough_spec,
    FileTree,
    )

from devportalbinary.binary import MetadataBackend

from devportalbinary.configuration import CONF_FILE_ENV_VAR

from djlibdep.test_double import LibdepServiceDouble


class IsChildPath(Matcher):

    def __init__(self, parent_path):
        super(IsChildPath, self).__init__()
        self._parent_path = parent_path

    def match(self, child_path):
        parent_segments = os.path.abspath(self._parent_path).split(os.sep)
        child_segments = os.path.abspath(child_path).split(os.sep)
        return Equals(parent_segments).match(
            child_segments[:len(parent_segments)])


class IsImage(Matcher):
    """Match a given image and ensure it is of size height, width and of
       image type kind
    """

    def __init__(self, width=None, height=None, kind=None):
        self.width = width
        self.height = height
        self.kind = kind

    def match(self, path):
        try:
            im = Image.open(path)
        except Exception as e:
            return Mismatch("could not open '%s': %s" % (path, e))
        is_good = True
        if self.width is not None:
            is_good &= (im.size[0] == self.width)
        if self.height is not None:
            is_good &= (im.size[1] == self.height)
        if self.kind is not None:
            is_good &= (im.format.upper() == self.kind.upper())
        # matcher expects "None" if everything is ok, else a Mismatch obj
        if is_good:
            return None
        else:
            return Mismatch(
                'exptected size=(%s, %s), kind=%s but got size=(%s, %s), '
                'kind=%s' % (self.width, self.height, self.kind,
                             im.size[0], im.size[1], im.format))


class ConfigSettings(Fixture):
    """Use a configuration file with different settings."""

    def __init__(self, *settings):
        """Construct a `ConfigSettings` fixture.

        :param *settings: A list of tuples ``(section, values)`` where
            ``section`` is the name of the configuration section and
            ``values`` is a dict mapping individual settings to their
            values.
        """
        super(ConfigSettings, self).__init__()
        self._settings = settings

    def setUp(self):
        super(ConfigSettings, self).setUp()
        # Set a temporary homedir so that any config on the user's
        # machine isn't picked up and the environment variable is used
        # instead.
        tempdir = self.useFixture(TempDir())
        config_file_path = os.path.join(tempdir.path, 'test.cfg')
        write_config_file(config_file_path, self._settings)
        self.useFixture(
            EnvironmentVariableFixture(CONF_FILE_ENV_VAR, config_file_path))


class LibdepFixture(Fixture):

    def __init__(self, data):
        super(LibdepFixture, self).__init__()
        self._data = data

    def setUp(self):
        super(LibdepFixture, self).setUp()
        double = self.useFixture(LibdepServiceDouble(self._data))
        self.useFixture(
            ConfigSettings(
                ('database', {'db_type': 'libdep-service',
                              'base_url': double.base_url,
                              })))


def LibsConfigSettings(test_libs):
    """Create a lib_overrides config file."""
    return ConfigSettings(
        ('libraries', {'overrides': 'library_overrides'}),
        ('library_overrides', test_libs),
        )


class MetadataFixture(Fixture):
    """Create a metadata file to use.

    :ivar path: The path to the directory containing the metadata file.
    """

    def __init__(self, metadata):
        """Create a ``MetadataFixture``.

        :param metadata: A dict of metadata.
        """
        self._metadata = metadata

    def setUp(self):
        super(MetadataFixture, self).setUp()
        files = [
            (MetadataBackend.METADATA_FILE, json.dumps(self._metadata)),
            ]
        tree = self.useFixture(FileTree(from_rough_spec(files)))
        self.path = tree.path
        self.metadata_path = os.path.join(
            self.path, MetadataBackend.METADATA_FILE)


class BinaryFileFixture(Fixture):
    """Create an ELF binary file."""

    def __init__(self, path):
        """Create a `BinaryFileFixture`.

        :param path: the path in which to put the file.
        """
        super(BinaryFileFixture, self).__init__()
        self.path = path

    def setUp(self):
        super(BinaryFileFixture, self).setUp()
        fname = "".join(random.sample(string.letters, 6))
        source_path = get_test_data_file_path('hello', 'hello')
        target_path = os.path.join(self.path, fname)
        def cleanup():
            if os.path.exists(target_path):
                os.unlink(target_path)
        self.addCleanup(cleanup)
        shutil.copyfile(source_path, target_path)


def get_test_data_dir_path(dirname):
    """Get the path to a directory in the test data."""
    return os.path.join(os.path.dirname(__file__), 'tests', 'data', dirname)


def get_test_data_file_path(dirname, filename):
    """Get the path to a file in the test data."""
    return os.path.join(get_test_data_dir_path(dirname), filename)


class BackendTests(TestCase):

    BACKEND = None

    def make_metadata(self, package_name=None, description=None, tagline=None,
                      categories=None, icons=None):
        if package_name is None:
            package_name = self.getUniqueString('package-name')
        metadata = {MetadataBackend.PACKAGE_NAME: package_name}
        if tagline is None:
            tagline = self.getUniqueString('tagline')
        metadata[MetadataBackend.TAGLINE] = tagline
        if description is not None:
            metadata[MetadataBackend.DESCRIPTION] = description
        if categories is not None:
            metadata[MetadataBackend.CATEGORIES] = categories
        if icons is not None:
            metadata[MetadataBackend.ICONS] = icons
        return metadata

    def make_backend(self, path=None, metadata=None):
        if path is None:
            path = self.useFixture(TempDir()).path
        if metadata is None:
            metadata = self.make_metadata()
        return self.BACKEND(path, metadata)

    def make_tree(self, rough_shape):
        return self.useFixture(FileTree(from_rough_spec(rough_shape))).path

    def want(self, tree):
        return self.BACKEND.want(self.make_tree(tree))


def make_config_section(key, values):
    lines = ['[%s]' % (key,)]
    for key, value in values.items():
        lines.append('%s=%s' % (key, value))
    lines.append('')
    return '\n'.join(lines)


def write_config_file(config_file_path, settings):
    """Write a config file to ``config_file_path``.

    :param config_file_path: The path to write a new config file to.
    :param settings: A list of tuples ``(section, values)`` where
        ``section`` is the name of the configuration section and
        ``values`` is a dict mapping individual settings to their
        values.
    """
    with open(config_file_path, 'w') as f:
        for section, values in settings:
            f.write(make_config_section(section, values))
            f.write('\n')
