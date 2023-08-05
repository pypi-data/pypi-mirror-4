# Copyright 2011-2012 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from .metadata import (
    get_excluded_package_files,
    get_icon_install_map,
    get_install_file,
    get_package_files,
    make_all_info_fn,
    make_want_fn,
    MetadataBackend,
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
            if filename.endswith(".user.js"):
                score = 20
            else:
                reason = 'File is not *.user.js: %r' % (filename,)
        else:
            reason = 'More files than just one *.user.js: %r' % (sorted(files),)
        return {'score': score, 'reason': reason}


want = make_want_fn(UnityWebappsBackend)
all_info = make_all_info_fn(UnityWebappsBackend)
