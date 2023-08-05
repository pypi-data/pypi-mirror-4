# Copyright 2011-2012 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

__all__ = [
    'backend_script',
    'convert_info',
    ]

from functools import wraps
import json
import sys

from pkgme.errors import PkgmeError
from pkgme.run_script import ScriptUserError


USER_ERROR_RETURN_CODE = ScriptUserError.RETURN_CODE


"""Base exception treated as errors for the end-user."""
BASE_USER_ERROR = PkgmeError


def convert_info(info):
    return dict((element.name, data) for element, data in info.items())


def backend_script(get_data):
    """Declare a function to be the core of a backend script.

    Essentially, our backend scripts are just things that print JSON,
    at least when all goes well.

    This wraps up the functions that return Python data so they have correct
    error handling.  It takes care of converting the data to JSON and printing
    it out.

    :param get_data: A function that returns a JSON-serializable object
        when passed a path to inspect.
    :return: A function that can be invoked as the 'main' of a backend script.
    """
    @wraps(get_data)
    def _wrapper(path, output_stream=None, error_stream=None):
        if output_stream is None:
            output_stream = sys.stdout
        if error_stream is None:
            error_stream = sys.stderr
        try:
            info = get_data(path)
        except BASE_USER_ERROR, e:
            error_stream.write(str(e))
            error_stream.write('\n')
            return USER_ERROR_RETURN_CODE
        else:
            json.dump(info, output_stream)
            return 0
    return _wrapper
