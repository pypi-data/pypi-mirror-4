from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import io
import itertools
import os
import re

from .utils.encoding import force_text


class Storage(object):
    """
    A base storage class, providing some default behaviors that all other
    storage systems can inherit or override, as necessary.
    """

    def __init__(self, chunk_size=None, **kwargs):
        self.chunk_size = chunk_size if not chunk_size is None else -1

        super(Storage, self).__init__(**kwargs)

    def _chunks(self, content):
        # Try to rewind the file
        try:
            content.seek(0)
        except (AttributeError, io.UnsupportedOperation):
            pass

        while True:
            data = content.read(self.chunk_size)
            if not data:
                break
            yield data

    # The following methods represent a public interface to private methods.
    # These shouldn't be overridden by subclasses unless absolutely necessary.

    def open(self, name, mode="rb"):
        """
        Retrieves the specified file from storage.
        """
        return self._open(name, mode)

    def save(self, name, content):
        """
        Saves new content to the file specified by name. The content should be
        a proper File object, ready to be read from the beginning.
        """
        # Get the proper name for the file, as it will actually be saved.
        if name is None:
            name = content.name

        name = self.get_available_name(name)
        name = self._save(name, content)

        # Store filenames with forward slashes, even on Windows
        return force_text(name.replace("\\", "/"))

    # These methods are part of the public API, with default implementations.

    def get_valid_name(self, name):
        """
        Returns a filename, based on the provided filename, that's suitable for
        use in the target storage system.
        """
        name = force_text(name).strip().replace(" ", "_")
        return re.sub(r"(?u)[^-\w.]", "", name)

    def get_available_name(self, name):
        """
        Returns a filename that's free on the target storage system, and
        available for new content to be written to.
        """
        dir_name, file_name = os.path.split(name)
        file_root, file_ext = os.path.splitext(file_name)

        # If the filename already exists, add an underscore and a number
        # (before the file extension, if one exists) to the filename until the
        # generated filename doesn't exist.
        count = itertools.count(1)

        while self.exists(name):
            # file_ext includes the dot.
            name = os.path.join(
                        dir_name,
                        "%s_%s%s" % (file_root, next(count), file_ext),
                    )

        return name

    # The following methods form the public API for storage systems, but with
    # no default implementations. Subclasses must implement *all* of these.

    def delete(self, name):
        """
        Deletes the specified file from the storage system.
        """
        raise NotImplementedError

    def exists(self, name):
        """
        Returns True if a file referened by the given name already exists in
        the storage system, or False if the name is available for a new file.
        """
        raise NotImplementedError

    def listdir(self, path):
        """
        Lists the contents of the specified path, returning a 2-tuple of lists;
        the first item being directories, the second item being files.
        """
        raise NotImplementedError

    def size(self, name):
        """
        Returns the total size, in bytes, of the file specified by name.
        """
        raise NotImplementedError

    def accessed_time(self, name):
        """
        Returns the last accessed time (as datetime object) of the file
        specified by name.
        """
        raise NotImplementedError

    def created_time(self, name):
        """
        Returns the creation time (as datetime object) of the file
        specified by name.
        """
        raise NotImplementedError

    def modified_time(self, name):
        """
        Returns the last modified time (as datetime object) of the file
        specified by name.
        """
        raise NotImplementedError

    # The following methods form the public API for storage systems, but with
    # no default implementations. Subclasses may implement them but are not
    # required too. Systems using them should handle NotImplemented.

    def url(self, name):
        """
        Returns an absolute URL where the file's contents can be accessed
        directly by a Web browser.
        """
        raise NotImplemented
