# Copyright 2011-2012 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""A pkgme backend that gets much of its data from MyApps.

The main idea behind this backend is that it looks for a file,
'devportal-metadata.json', created with data provided by users of MyApps.  It
then uses this data, along with inferences from submitted files to create a
Debian package.
"""

__all__ = [
    'MetadataBackend',
    ]

import json
import os
import tempfile

import Image

from pkgme.info_elements import (
    ApplicationName,
    Architecture,
    BuildDepends,
    Categories,
    Depends,
    Description,
    Distribution,
    Executable,
    ExplicitCopyright,
    ExtraControlBinaryFields,
    ExtraFiles,
    ExtraFilesFromPaths,
    ExtraTargets,
    Icon,
    License,
    Maintainer,
    PackageName,
    Homepage,
    Section,
    TagLine,
    Version,
    WorkingDirectory,
    )
from pkgme.package_files import (
    DEBIAN_DIR,
    Desktop,
    )
from pkgme.project_info import DictInfo

from .backend import (
    backend_script,
    convert_info,
    )
from .utils import (
    first_path_component,
    get_latest_stable_ubuntu_distroseries,
    )


# XXX: is this the right place?
LINTIAN_OVERRIDES_TEMPLATE = """
#Partner package contents belong in /opt
%(package_name)s: dir-or-file-in-opt

#Partner package may content embedded libs
%(package_name)s: embedded-library

#Bullet lists
%(package_name)s: extended-description-line-too-long
"""


# map devportals license understanding to the common-licenses of debian
# see also src/devportal/models.py:1324
LICENSE_MAPPING = {
    'Apache License' : 'Apache-2.0',
    'BSD License (Simplified)' : 'BSD',
    'GNU GPL v2' : 'GPL-2',
    "GNU GPL v3" : 'GPL-3',
    "GNU LGPL v2.1" : "LGPL-2.1",
    "GNU LGPL v3" :  "LGPL-3",
    "Artistic License 1.0" : "Artistic",
    "Proprietary" : "Proprietary\n All rights reserved.",
}

DEFAULT_ICON_THEME = 'hicolor'


def get_icon_install_map(icons, icon_theme=None):
    """Get the install map for a set of icons.

    Returns the install map to install `icons` to an icon
    theme.

    :param icons: a dict mapping resolution to icon source path.
    :param icon_theme: if supplied the name of the icon theme to
        install to, or None for the default.
    """
    if icon_theme is None:
        icon_theme = DEFAULT_ICON_THEME
    installation = []
    for resolution, path in icons.items():
        # XXX: This means that the basename of 'path' has to match the value
        # of the Icon field in the desktop file.  Seems fragile.
        installation.append((path,
            'usr/share/icons/{0}/{1}/apps'.format(icon_theme, resolution)))
    return installation


def get_desktop_install_map(package_name):
    """Get the install map to install the .desktop file for `package_name`."""
    desktop = 'debian/%s.desktop' % (package_name,)
    return [(desktop, 'usr/share/applications')]


def get_files_install_map(install_basedir, path):
    """Get the install map needed to install a set of file.

    The returned map would cause debhelper to install all files
    below `path` to `install_basedir`.
    """
    installation = []
    # Make it a relative path to fit with the standard for install files
    basedir = install_basedir.lstrip('/')
    # Sorting not actually needed for functionality, but makes the tests more
    # reliable.
    for filename in sorted(os.listdir(path)):
        if filename in (DEBIAN_DIR, MetadataBackend.METADATA_FILE):
            # We don't want to install the 'debian/' directory or the metadata
            # file.
            continue
        installation.append((filename, basedir))
    return installation


def format_install_map(install_map):
    """Take an install map and generate the corresponding install file.

    An install file is a list of tuples of (src, dst) where src is
    the location of the file within the source package, and dst is
    where it should end up during the install phase.

    :return: a string containing the install file contents needed
        to install according to the supplied install map.
    """
    # Sorting not actually needed for functionality, but makes the tests more
    # reliable.
    lines = sorted('%s %s' % (src, dst) for (src, dst) in install_map)
    # Ending the file with a newline is basic good manners.
    lines.append('')
    return '\n'.join(lines)


def get_install_file(install_basedir, path, extra_mappings=None):
    """Generate the install file.

    Installs the files in `path` to `install_basedir`.

    If `extra_mappings` is supplied the files it includes will
    also be installed. The format is a list of tuples of (src, dst)
    where src is the path of the file in the source package and
    dst is the target location, e.g.

        [('debian/foo', 'usr/share/bar')]
    """
    install_map = get_files_install_map(install_basedir, path)
    if extra_mappings:
        install_map += extra_mappings
    return format_install_map(install_map)


def get_desktop_file(package_name, application_name, executable,
                     tagline=None, categories=None, icon=None,
                     working_directory=None):
    """Get the desktop file for the package.

    :return: A ``Desktop``.
    """
    categories_string = ""
    if categories:
        # desktop files expect a trailing ";"
        categories_string = ";".join(categories) + ";"
    info = {
        PackageName.name: package_name,
        ApplicationName.name: application_name,
        Executable.name: executable,
        TagLine.name: tagline,
        Categories.name: categories_string,
        Icon.name: icon,
        WorkingDirectory.name: working_directory,
        }
    return Desktop.from_info(DictInfo(info))


def convert_icon(icon_path, new_size):
    """Takes a icon_path and converts it to the new size

    :return: path of the newly created icon of the requested size
    """
    im = Image.open(icon_path)
    tmp_icon = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    size = get_icon_size_from_string(new_size)
    out = im.resize((size, size))
    out.save(tmp_icon.name)
    return tmp_icon.name


def get_icon_size_from_string(s):
    """Return a integer size from a string of the form 'WxH' ('48x48')

    :raise ValueError: if we're given a non-square size.

    :return: The size of the icon.
    """
    if "x" not in s:
        return int(s)
    w, h = s.split("x")
    if w != h:
        raise ValueError("Got ('%s', '%s') size, but only square sizes "
                         "are supported" % (w, h))
    return int(w)


def get_package_files(path, excluded_files):
    """Return a set of files under path that belong to the package.

    Only returns the top level, does not recurse.
    """
    return set(os.listdir(path)) - excluded_files


def get_excluded_package_files(cls, metadata):
    """Get the files that shouldn't be considered as package files for `cls`.

    :return: a set of filenames that shouldn't be considered package files.
    """
    # XXX: This implies that we're doing exact string matching on the
    # paths in the metadata and the results of os.listdir.  We actually
    # want to exclude the icons if they are the same file, not if the
    # strings happen to be equal.
    excluded_files = set([cls.METADATA_FILE, 'debian'])
    excluded_files |= set(map(first_path_component,
        filter(lambda x: not os.path.isabs(x),
            metadata.get(cls.ICONS, {}).values())))
    return excluded_files


def load_json(path):
    """Load JSON from `path`.

    :param path: the path to load the JSON from.
    :return: (json, err) where json is the deserialized contents of the file,
        or None if it didn't exist or didn't contain json. If json is
        None then err will be a description of why it couldn't be loaded.
    """
    if not os.path.exists(path):
        return None, 'No metadata file'
    try:
        with open(path) as f:
            metadata = json.load(f)
    except ValueError:
        # Not a JSON file.
        return None, 'Metadata file is not valid JSON'
    return metadata, None


def want_single_file_with_metadata(backend, path, metadata, predicate,
                                   match_score,
                                   mismatch_message, too_many_message):
    excluded_files = get_excluded_package_files(backend, metadata)
    files = list(get_package_files(path, excluded_files))
    # By default, we don't want it and give no reason.  Sane default in
    # case of buggy code below.
    score = 0
    reason = None
    if len(files) == 0:
        reason = 'No files found, just metadata'
    elif len(files) == 1:
        filename = files[0]
        if predicate(filename):
            score = match_score
        else:
            reason = '%s: %r' % (mismatch_message, filename)
    else:
        reason = '%s: %r' % (too_many_message, sorted(files))
    return {'score': score, 'reason': reason}


def _has_extensions(extensions):
    def _filename_has_extensions(filename):
        for ext in extensions:
            if filename.endswith(ext):
                return True
        return False
    return _filename_has_extensions


def want_single_file_by_extension(cls, path, metadata, extensions, name, score=20):
    return want_single_file_with_metadata(
        cls, path, metadata,
        _has_extensions(extensions),
        score,
        "File is not %s" % (name,),
        "More files than just %s" % (name,),
        )


class MetadataBackend(object):
    """A backend that is mostly powered by metadata from MyApps."""

    # Where the metadata file lives.
    METADATA_FILE = 'devportal-metadata.json'

    # Keys found in the metadata file.
    # XXX: These duplicate the schema found in pkgme-service.
    APPLICATION_NAME = 'name'
    CATEGORIES = 'categories'
    DESCRIPTION = 'description'
    ICONS = 'icons'
    LICENSE = 'license'
    MAINTAINER = 'maintainer'
    PACKAGE_NAME = 'package_name'
    SUGGESTED_PACKAGE_NAME = 'suggested_package_name'
    SUGGESTED_VERSION = 'suggested_version'
    TAGLINE = 'tagline'
    # its "Homepage" in the deb package but "website" on the devportal
    HOMEPAGE = 'website'

    # the icon size that must be present
    REQUIRED_ICON_SIZE = '48x48'

    # the basedir
    INSTALL_BASEDIR = '/opt/'

    def __init__(self, path, metadata):
        """Construct a ``MetadataBackend``."""
        self.path = path
        self.metadata = metadata

    def _calculate_info_element(self, info_element, *args, **kwargs):
        PREFIX = 'get_'
        method = getattr(self, '%s%s' % (PREFIX, info_element.name))
        return method(*args, **kwargs)

    def get_application_name(self):
        """Get the application name for the package.

        Used in the desktop file.
        """
        # XXX: Probably can assume that this is always present, since MyApps
        # requires it.  Leaving as optional for now on the hunch that it will
        # smooth out the deployment process or at least the branch size.
        try:
            return self.metadata[self.APPLICATION_NAME]
        except KeyError:
            try:
                return self._calculate_info_element(
                    PackageName).capitalize()
            except AssertionError:
                raise AssertionError("Could not determine application name")

    def get_architecture(self):
        """Get the architecture for the package.

        :return: The architecture tag, or None if no architecture is
            specified.
        """
        raise NotImplementedError(self.get_architecture)

    def get_build_depends(self):
        """Get the build dependencies of the package."""
        raise NotImplementedError(self.get_build_depends)

    def get_depends(self):
        """Get the dependencies for the package."""
        raise NotImplementedError(self.depends)

    def get_description(self):
        """Get the package description."""
        return self.metadata.get(self.DESCRIPTION, '')

    def get_distribution(self):
        return get_latest_stable_ubuntu_distroseries()

    def get_executable(self, package_name):
        """Return the path to the executable."""
        raise NotImplementedError(self.get_executable)

    def get_explicit_copyright(self):
        return None

    def get_extra_control_binary_fields(self):
        return None

    def get_extra_targets(self, package_name):
        """Return any extra debian/rules targets. """
        return ""

    def _get_lintian_overrides(self, package_name):
        return LINTIAN_OVERRIDES_TEMPLATE % {'package_name' : package_name,}

    def _get_install_basedir(self, package_name):
        return os.path.join(self.INSTALL_BASEDIR, package_name)

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
        extra_mappings = get_icon_install_map(icons)
        extra_mappings += get_desktop_install_map(package_name)
        install_file = get_install_file(install_basedir, self.path,
                extra_mappings=extra_mappings)
        executable = self.get_executable(package_name)
        application_name = self._calculate_info_element(
            ApplicationName)
        if self.ICONS in self.metadata:
            icon = package_name
        else:
            icon = None
        desktop_file = get_desktop_file(
            package_name,
            application_name,
            executable,
            tagline=self.metadata.get(self.TAGLINE, ''),
            categories=self.metadata.get(self.CATEGORIES, ''),
            icon=icon,
            working_directory=install_basedir)
        lintian_override_content = self._get_lintian_overrides(package_name)
        return {
            # XXX: Hardcoded literal attack!
            'debian/install': install_file,
            'debian/%s.desktop' % (package_name,): desktop_file.get_contents(),
            'debian/%s.lintian-overrides' % (package_name,) : lintian_override_content,
            }

    def get_extra_files_from_paths(self, package_name):
        """Get extra, binary files for the package."""
        extra_files = self._get_extra_icon_files_from_paths(package_name)
        return extra_files

    def _get_extra_icon_files_from_paths(self, package_name):
        icon_map = self._get_icon_map(package_name)
        return dict(icon_map.values())

    def _pick_closest_icon_resolution_for_size(self, icon_sizes_list, size):
        """Find the best matching resolution for the given "size"

        :return: a string with the closest icon match
        """
        size_as_int = get_icon_size_from_string(size)
        sorted_sizes = sorted(icon_sizes_list, key=get_icon_size_from_string)
        # try to find the first bigger icon than "size"
        for size_str in sorted_sizes:
            if get_icon_size_from_string(size_str) > size_as_int:
                return size_str
        # if nothing bigger is found, return the biggest we have
        return sorted_sizes[-1]

    def _ensure_required_icon_size(self, required_size):
        """ Ensure that the size "required_size" is part of the ICONS
            metadata and create a new icon if needed.

            Note that this modifies metadata[self.ICONS].
        """
        icons = self.metadata.get(self.ICONS, {})
        if not icons or required_size in icons:
            return
        best_resolution = self._pick_closest_icon_resolution_for_size(
            icons.keys(), required_size)
        new_path = convert_icon(icons[best_resolution], required_size)
        icons[required_size] = new_path
        self.metadata[self.ICONS] = icons

    def _get_icon_map(self, package_name, rename=True):
        """Return a dict mapping resolutions to paths.

        Each resolution is mapped to two paths: a relative debian path, which
        is where pkgme will store the icon, and an absolute path, which is
        where the icon can be found.

        Because the icons will be installed from the relative debian path, the
        basename of that path sans extension *must* be equal to the value of
        the Icon field in the desktop file, which is set to the package name
        in the default implementation. If rename=False is passed, then the
        basename will be whatever the basename of the input icon is.

        :param rename: whether to rename the icons to match the package
            name. Default is to rename (True).
        :return: {resolution: (dst, src), ...}
        """
        # ensure that we have the required icon size
        self._ensure_required_icon_size(self.REQUIRED_ICON_SIZE)

        icon_map = {}
        for resolution, path in self.metadata.get(self.ICONS, {}).items():
            src = os.path.normpath(os.path.join(self.path, path))
            orig_basename, ext = os.path.splitext(path)
            if rename:
                basename = package_name
            else:
                basename = orig_basename
            dst = 'debian/icons/%s/%s%s' % (resolution, basename, ext)
            icon_map[resolution] = (dst, src)

        return icon_map

    def get_homepage(self):
        return self.metadata.get(self.HOMEPAGE, None)

    def get_license(self):
        devportal_license = self.metadata.get(self.LICENSE, "unknown")
        return LICENSE_MAPPING.get(devportal_license, devportal_license)

    def get_maintainer(self):
        return self.metadata.get(self.MAINTAINER, None)

    def get_package_name(self):
        """Get the package name."""
        package_name_sources = [
            self.PACKAGE_NAME,
            self.SUGGESTED_PACKAGE_NAME,
            self.APPLICATION_NAME,
            ]
        for source in package_name_sources:
            package_name = self.metadata.get(source, None)
            if package_name:
                return package_name
        raise AssertionError("Could not determine package name")

    def get_section(self):
        return None

    def get_version(self):
        """Get the version of the package."""
        return self.metadata.get(self.SUGGESTED_VERSION, None)

    @classmethod
    def get_metadata_path(cls, path):
        return os.path.join(path, cls.METADATA_FILE)

    @classmethod
    def get_metadata(cls, path):
        """Get the metadata for this backend.

        Looks for the metadata in a file called ``METADATA_FILE`` in the
        directory given to the constructor.

        :return: A dict of metadata.
        """
        metadata, err = load_json(cls.get_metadata_path(path))
        if metadata is None:
            raise AssertionError(err)
        return metadata

    def get_info(self):
        """Return a dict of InfoElements given 'metadata'.

        This is the work-horse method of the backend. It takes a dict of
        metadata, as extracted from a devportal-metadata.json file, and
        converts it into a dictionary mapping InfoElements to their actual
        values.

        This dictionary will then be dumped as the JSON output of 'all_info',
        substituting the InfoElements for their names.
        """
        COMPULSORY_ELEMENTS = [
            BuildDepends,
            Depends,
            Description,
            License,
            PackageName,
            ]
        OPTIONAL_ELEMENTS = [
            Architecture,
            Distribution,
            ExplicitCopyright,
            ExtraControlBinaryFields,
            Maintainer,
            Section,
            Version,
            Homepage,
            ]
        PACKAGE_NAME_ELEMENTS = [
            ExtraFiles,
            ExtraFilesFromPaths,
            ExtraTargets,
            ]
        info = {}
        for element in COMPULSORY_ELEMENTS:
            info[element] = self._calculate_info_element(element)
        for element in OPTIONAL_ELEMENTS:
            value = self._calculate_info_element(element)
            if value:
                info[element] = value
        # Special-case those elements that need the package name
        package_name = PackageName.clean(info[PackageName])
        for element in PACKAGE_NAME_ELEMENTS:
            value = self._calculate_info_element(element, package_name)
            if value:
                info[element] = value
        return info

    @classmethod
    def want(cls, path):
        """How relevant this backend is."""
        metadata, err = load_json(cls.get_metadata_path(path))
        if err is not None:
            return {'score': 0, 'reason': err}
        return cls.want_with_metadata(path, metadata)

    @classmethod
    def want_with_metadata(self, path, metadata):
        """How relevant this backend is, after metadata has been found.

        Specific backends should override this.
        """
        raise NotImplementedError(self.want_with_metadata)


def make_want_fn(backend_cls):
    def metadata_want(path):
        return backend_cls.want(path)
    metadata_want.__name__ = '{}_want'.format(backend_cls.__name__)
    return backend_script(metadata_want)


def make_all_info_fn(backend_cls):
    def metadata_all_info(path):
        metadata = backend_cls.get_metadata(path)
        backend = backend_cls(path, metadata)
        info = backend.get_info()
        return convert_info(info)
    metadata_all_info.__name__ = '{}_all_info'.format(backend_cls.__name__)
    return backend_script(metadata_all_info)
