# Copyright 2011-2012 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from .metadata import (
    get_icon_install_map,
    get_install_file,
    make_all_info_fn,
    make_want_fn,
    MetadataBackend,
    want_single_file_by_extension,
    )


ICON_THEME = 'unity-webapps-applications'


def get_webapp_icon_install_map(icons):
    install_map = get_icon_install_map(icons, icon_theme=ICON_THEME)
    special_size = UnityWebappsBackend.REQUIRED_ICON_SIZE
    if special_size in icons:
        # The hicolor icon theme uses 2d directory names
        install_map += get_icon_install_map(
            {'{0}x{0}'.format(special_size): icons[special_size]})
    return install_map


class UnityWebappsBackend(MetadataBackend):
    """A backend for Unity Webapps."""

    METADATA_FILE = 'manifest.json'

    INSTALL_BASEDIR = '/usr/share/unity-webapps/userscripts/'

    DESCRIPTION = 'description'
    HOMEPAGE = 'homepage'
    ICONS = 'icons'
    INCLUDES = 'includes'
    INTEGRATION_VERSION = 'integration-version'
    LICENSE = 'license'
    MAINTAINER = 'maintainer'
    NAME = 'name'
    PACKAGE_NAME = 'package-name'
    PACKAGE_NAME_PREFIX = 'unity-webapps-'
    REQUIRED_ICON_SIZE = '48'

    def get_architecture(self):
        return 'all'

    def get_build_depends(self):
        return 'debhelper (>=7)'

    def get_depends(self):
        return ('unity-webapps-common, '
                'xdg-utils, ${misc:Depends}')

    def get_package_name(self):
        package_name = self.metadata.get(self.PACKAGE_NAME)
        if not package_name.startswith(self.PACKAGE_NAME_PREFIX):
            package_name = self.PACKAGE_NAME_PREFIX + package_name
        return package_name

    def get_distribution(self):
        return 'quantal'

    def get_section(self):
        return 'web'

    def get_version(self):
        """Get the version of the package."""
        return self.metadata.get(self.INTEGRATION_VERSION, None)

    def get_extra_control_binary_fields(self):
        name = self.metadata.get(self.NAME)
        includes = self.metadata.get(self.INCLUDES)
        return ("XB-Ubuntu-Webapps-Includes: {0}\n"
                "XB-Ubuntu-Webapps-Name: {1}").format(
                    ";".join(includes), name)

    def get_extra_files(self, package_name):
        """Get the extra files for the package.

        Assumes that the only extra files are a desktop file and an install
        file.  Delegates to ``get_desktop_file`` for the desktop file.
        """
        install_basedir = self._get_install_basedir(package_name)
        icons = {}
        icon_map = self._get_icon_map(package_name)
        for resolution in icon_map:
            dst, src = icon_map[resolution]
            icons[resolution] = dst
        extra_mappings = get_webapp_icon_install_map(icons)
        install_file = get_install_file(install_basedir, self.path,
            extra_mappings=extra_mappings)
        return {
            # XXX: Hardcoded literal attack!
            'debian/install': install_file,
            }

    @classmethod
    def want_with_metadata(cls, path, metadata):
        return want_single_file_by_extension(
            cls, path, metadata, ['.user.js'], '*.user.js')


want = make_want_fn(UnityWebappsBackend)
all_info = make_all_info_fn(UnityWebappsBackend)
