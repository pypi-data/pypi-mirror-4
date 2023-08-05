# Copyright 2011-2012 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import json

from testtools import TestCase
from treeshape import (
    CONTENT,
    FileTree,
    )

from devportalbinary.unity_webapps import (
    get_webapp_icon_install_map,
    UnityWebappsBackend,
    )


class UnityBackendTests(TestCase):

    def get_metadata_tree(self, metadata=None):
        if metadata is None:
            metadata = {}
        return {UnityWebappsBackend.METADATA_FILE:
                {CONTENT: json.dumps(metadata)}}

    def test_want_with_metadata(self):
        # If we detect the metadata file and a .user.js, then we score 20.
        tree = self.get_metadata_tree()
        filename = self.getUniqueString() + ".user.js"
        tree[filename] = {}
        tempdir = self.useFixture(FileTree(tree))
        self.assertEqual(20, UnityWebappsBackend.want(tempdir.path)['score'])

    def test_want_with_no_metadata(self):
        # If we detect no metadata file we score 0
        filename = self.getUniqueString() + ".user.js"
        tree = {filename: {}}
        tempdir = self.useFixture(FileTree(tree))
        want = UnityWebappsBackend.want(tempdir.path)
        self.assertEqual(0, want['score'])
        self.assertEqual('No metadata file', want['reason'])

    def test_want_with_no_userscript(self):
        # If we detect no userscript file we score 0
        tree = self.get_metadata_tree()
        tempdir = self.useFixture(FileTree(tree))
        want = UnityWebappsBackend.want(tempdir.path)
        self.assertEqual(0, want['score'])
        self.assertEqual('No files found, just metadata', want['reason'])

    def test_want_with_non_userscript(self):
        # If we detect something that isn't a userscript file we score 0
        tree = self.get_metadata_tree()
        filename = self.getUniqueString() + ".something"
        tree[filename] = {}
        tempdir = self.useFixture(FileTree(tree))
        want = UnityWebappsBackend.want(tempdir.path)
        self.assertEqual(0, want['score'])
        self.assertEqual('File is not *.user.js: %r' % filename,
                want['reason'])

    def test_want_with_icons(self):
        # If we detect something that isn't a userscript file we score 0
        tree = self.get_metadata_tree(dict(icons={64:'icons/blah.png'}))
        tree['icons/'] = {}
        filename = self.getUniqueString() + ".user.js"
        tree[filename] = {}
        tempdir = self.useFixture(FileTree(tree))
        want = UnityWebappsBackend.want(tempdir.path)
        self.assertEqual(20, want['score'])

    def test_get_architecture(self):
        metadata = dict()
        tempdir = self.useFixture(FileTree({}))
        backend = UnityWebappsBackend(tempdir.path, metadata)
        self.assertEqual('all', backend.get_architecture())

    def test_get_build_depends(self):
        metadata = dict()
        tempdir = self.useFixture(FileTree({}))
        backend = UnityWebappsBackend(tempdir.path, metadata)
        self.assertEqual('debhelper (>=7)',
                backend.get_build_depends())

    def test_get_depends(self):
        metadata = dict()
        tempdir = self.useFixture(FileTree({}))
        backend = UnityWebappsBackend(tempdir.path, metadata)
        self.assertEqual(
            'unity-webapps-common, xdg-utils, ${misc:Depends}',
            backend.get_depends())

    def test_get_package_name(self):
        tempdir = self.useFixture(FileTree({}))
        package_name = 'unity-webapps-foo'
        metadata = {'package-name': package_name}
        backend = UnityWebappsBackend(tempdir.path, metadata)
        self.assertEqual(package_name, backend.get_package_name())

    def test_get_package_name_adds_prefix(self):
        tempdir = self.useFixture(FileTree({}))
        metadata = {'package-name': 'foo'}
        backend = UnityWebappsBackend(tempdir.path, metadata)
        self.assertEqual('unity-webapps-foo',
                backend.get_package_name())

    def test_get_distribution(self):
        tempdir = self.useFixture(FileTree({}))
        metadata = {}
        backend = UnityWebappsBackend(tempdir.path, metadata)
        self.assertEqual('quantal', backend.get_distribution())

    def test_get_section(self):
        tempdir = self.useFixture(FileTree({}))
        metadata = {}
        backend = UnityWebappsBackend(tempdir.path, metadata)
        self.assertEqual('web', backend.get_section())

    def test_get_version(self):
        tempdir = self.useFixture(FileTree({}))
        metadata = {'integration-version': '1.0'}
        backend = UnityWebappsBackend(tempdir.path, metadata)
        self.assertEqual('1.0', backend.get_version())

    def test_get_extra_files(self):
        filename = 'foo.user.js'
        tempdir = self.useFixture(FileTree({filename: {}}))
        package_name = 'bar'
        backend = UnityWebappsBackend(tempdir.path, {})
        extra_files = backend.get_extra_files(package_name)
        self.assertEqual(
            {'debian/install':
                '{0} usr/share/unity-webapps/userscripts/{1}\n'.format(
                    filename, package_name)},
            extra_files)

    def test_get_extra_files_with_icons(self):
        filename = 'foo.user.js'
        tempdir = self.useFixture(FileTree({filename: {}}))
        package_name = 'bar'
        metadata = {UnityWebappsBackend.ICONS: {'48': 'foo.png'}}
        backend = UnityWebappsBackend(tempdir.path, metadata)
        extra_files = backend.get_extra_files(package_name)
        self.assertEqual(
            {'debian/install':
                ('debian/icons/48/foo.png usr/share/icons/hicolor/48x48/apps\n'
                 'debian/icons/48/foo.png usr/share/icons/'
                    'unity-webapps-applications/48/apps\n'
                 '{0} usr/share/unity-webapps/userscripts/{1}\n'
                    ).format(
                    filename, package_name)},
            extra_files)

    def test_get_extra_control_binary_fields(self):
        metadata = {
            'name': 'Foo',
            'includes': ['*.foo.com', 'foo.com'],
        }
        tempdir = self.useFixture(FileTree({}))
        backend = UnityWebappsBackend(tempdir.path, metadata)
        self.assertEqual(
            ('XB-Ubuntu-Webapps-Includes: *.foo.com;foo.com\n'
             'XB-Ubuntu-Webapps-Name: Foo'),
            backend.get_extra_control_binary_fields())


class GetWebappIconInstallMapTests(TestCase):

    def test_includes_both_locations(self):
        icons = {'48': 'foo.png'}
        self.assertEqual(
            [('foo.png', 'usr/share/icons/unity-webapps-applications/48/apps'),
             ('foo.png', 'usr/share/icons/hicolor/48x48/apps')],
            get_webapp_icon_install_map(icons))

    def test_allows_special_size_missing(self):
        icons = {'64': 'foo.png'}
        self.assertEqual(
            [('foo.png', 'usr/share/icons/unity-webapps-applications/64/apps')],
            get_webapp_icon_install_map(icons))
