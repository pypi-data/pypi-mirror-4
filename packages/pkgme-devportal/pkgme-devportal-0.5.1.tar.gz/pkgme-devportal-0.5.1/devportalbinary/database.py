# Copyright 2011 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from .configuration import load_configuration
from .utils import download_file

from libdep_service_client.client import Client

# Shut up pyflakes.  Imported because other things use this.
download_file


def get_dependency_database():
    """Return an object that can get dependencies."""
    options = load_configuration()
    return Client(options.database_base_url)
