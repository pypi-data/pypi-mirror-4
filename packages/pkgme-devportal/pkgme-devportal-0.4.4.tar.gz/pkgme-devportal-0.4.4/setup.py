# Copyright 2011 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import distribute_setup
# What is specified here is the minimum version, and the version
# that will be installed if there isn't one already. We specify
# it so that we can update distribute_setup without it implying
# that we require the latest version, which can cause unnecessary
# updating, and can fail if there is a version conflict.
# If we do require a higher minimum version then update it here
# and ensure that distribute_setup is at least as new as that
# version.
distribute_setup.use_setuptools(version='0.6.10')

from setup_helpers import (
    description,
    get_version,
    )
from setuptools import setup, find_packages


__version__ = get_version('devportalbinary/__init__.py')

setup(
    name='pkgme-devportal',
    version=__version__,
    packages=find_packages(),
    include_package_data=True,
    maintainer='pkgme developers',
    maintainer_email='pkgme-devs@lists.launchpad.net',
    description=description('README'),
    license='AGPLv3',
    url='http://launchpad.net/pkgme-devportal',
    download_url='https://launchpad.net/pkgme-devportal/+download',
    test_suite='devportalbinary.tests',
    install_requires = [
        'bzr',
        'configglue',
        'launchpadlib',
        'PIL',
        'pkgme>=0.4.1',
        'fixtures',
        'storm',
        ],
    entry_points = {
        'console_scripts': [
            'dump-apt-file-db=devportalbinary.aptfile:dump_apt_file_db',
            'fetch-symbol-files=devportalbinary.database:main',
            'guess-executable=devportalbinary.binary:print_executable',
            'guess-deps=devportalbinary.binary:print_dependencies',
            ],
        'pkgme.get_backends_path': ['binary=devportalbinary:get_backends_path'],
        },
    extras_require = {
        'testing': [
            'postgresfixture',
            'testresources',
            'testtools',
            'treeshape',
            ],
        },
    # Auto-conversion to Python 3.
    use_2to3=True,
    )
