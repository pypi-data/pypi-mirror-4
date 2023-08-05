from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import os

import six

from .encoding import force_text


# Under Python 2, define our own abspath function that can handle joining
# unicode paths to a current working directory that has non-ASCII characters
# in it.  This isn't necessary on Windows since the Windows version of abspath
# handles this correctly. It also handles drive letters differently than the
# pure Python implementation, so it's best not to replace it.
if six.PY3 or os.name == "nt":
    abspathu = abspath
else:
    def abspathu(path):
        """
        Version of os.path.abspath that uses the unicode representation
        of the current working directory, thus avoiding a UnicodeDecodeError
        in join when the cwd has non-ASCII characters.
        """
        if not os.path.isabs(path):
            path = os.path.join(os.getcwdu(), path)
        return os.path.normpath(path)


def safe_join(base, *paths):
    """
    Joins one or more path components to the base path component intelligently.
    Returns a normalized, absolute version of the final path.

    The final path must be located inside of the base path component (otherwise
    a ValueError is raised).
    """
    base = force_text(base)
    paths = [force_text(p) for p in paths]
    final_path = abspathu(os.path.join(base, *paths))
    base_path = abspathu(base)
    # Ensure final_path starts with base_path (using normcase to ensure we
    # don't false-negative on case insensitive operating systems like Windows),
    # further, one of the following conditions must be true:
    #  a) The next character is the path separator (to prevent conditions like
    #     safe_join("/dir", "/../d"))
    #  b) The final path must be the same as the base path.
    #  c) The base path must be the most root path (meaning either "/" or "C:\\")
    if (
        not os.path.normcase(final_path).startswith(
                                        os.path.normcase(base_path + os.sep))
        and os.path.normcase(final_path) != os.path.normcase(base_path)
        and os.path.dirname(
            os.path.normcase(base_path)) != os.path.normcase(base_path)):
        raise ValueError('The joined path (%s) is located outside of the base '
                         'path component (%s)' % (final_path, base_path))
    return final_path
