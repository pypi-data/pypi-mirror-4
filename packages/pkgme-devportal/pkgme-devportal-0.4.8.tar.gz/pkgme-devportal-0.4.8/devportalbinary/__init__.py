# Copyright 2011 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from pkg_resources import resource_filename

__all__ = [
    '__version__',
    'get_backends_path',
    ]


__version__ = '0.4.8'


def get_backends_path():
    return resource_filename(__name__, 'backends')
