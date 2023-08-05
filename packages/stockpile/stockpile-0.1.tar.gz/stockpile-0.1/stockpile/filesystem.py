from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import datetime
import errno
import os

from .base import Storage
from .exceptions import SuspiciousOperation
from .hashed import HashedMixin
from .utils import locks
from .utils.encoding import filepath_to_uri
from .utils._os import abspathu, safe_join

try:
    from urllib.parse import urljoin
except ImportError:     # Python 2
    from urlparse import urljoin


__all__ = ["FileSystem"]


class FileSystem(Storage):
    """
    Standard filesystem storage
    """

    def __init__(self, location, base_url=None, permissions=None, **kwargs):
        self.base_location = location
        self.location = abspathu(self.base_location)
        self.base_url = base_url
        self.permissions = permissions

        super(FileSystem, self).__init__(**kwargs)

    def _open(self, name, mode="rb"):
        return open(self.path(name), mode)

    def _save(self, name, content):
        full_path = self.path(name)

        # Create any intermediate directories that do not exist.
        # Note that there is a race between os.path.exists and os.makedirs:
        # if os.makedirs fails with EEXIST, the directory was created
        # concurrently, and we can continue normally. Refs #16082.
        directory = os.path.dirname(full_path)
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
        if not os.path.isdir(directory):
            raise IOError("%s exists and is not a directory." % directory)

        # There's a potential race condition between get_available_name and
        # saving the file; it's possible that two threads might return the
        # same name, at which point all sorts of fun happens. So we need to
        # try to create the file, but if it already exists we have to go back
        # to get_available_name() and try again.

        while True:
            try:
                # This fun binary flag incantation makes os.open throw an
                # OSError if the file already exists before we open it.
                flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                         getattr(os, "O_BINARY", 0))

                # The current umask value is masked out by os.open!
                fd = os.open(full_path, flags, 0o666)

                try:
                    locks.lock(fd, locks.LOCK_EX)
                    _file = None

                    for chunk in self._chunks(content):
                        if _file is None:
                            mode = "wb" if isinstance(chunk, bytes) else "wt"
                            _file = os.fdopen(fd, mode)
                        _file.write(chunk)
                finally:
                    locks.unlock(fd)

                    if _file is not None:
                        _file.close()
                    else:
                        os.close(fd)
            except OSError as e:
                if e.errno == errno.EEXIST:
                    # Ooops, the file exists. We need a new file name.
                    name = self.get_available_name(name)
                    full_path = self.path(name)
                else:
                    raise
            else:
                # OK, the file save worked. Break out of the loop.
                break

        if not self.permissions is None:
            os.chmod(full_path, self.permissions)

        return name

    def delete(self, name):
        name = self.path(name)

        # If the file exists, delete it from the filesystem.
        # Note that there is a race between os.path.exists and os.remove:
        # if os.remove fails with ENOENT, the file was removed
        # concurrently, and we can continue normally.
        if os.path.exists(name):
            try:
                os.remove(name)
            except OSError as e:
                if e.errno != errno.ENOENT:
                    raise

    def exists(self, name):
        return os.path.exists(self.path(name))

    def listdir(self, path):
        path = self.path(path)
        directories, files = [], []
        for entry in os.listdir(path):
            if os.path.isdir(os.path.join(path, entry)):
                directories.append(entry)
            else:
                files.append(entry)
        return directories, files

    def path(self, name):
        try:
            path = safe_join(self.location, name)
        except ValueError:
            raise SuspiciousOperation(
                        "Attempted access to '%s' denied." % name,
                    )
        return os.path.normpath(path)

    def size(self, name):
        return os.path.getsize(self.path(name))

    def accessed_time(self, name):
        return datetime.fromtimestamp(os.path.getatime(self.path(name)))

    def created_time(self, name):
        return datetime.fromtimestamp(os.path.getctime(self.path(name)))

    def modified_time(self, name):
        return datetime.fromtimestamp(os.path.getmtime(self.path(name)))

    def url(self, name):
        if self.base_url is None:
            return super(FileSystem, self).url(name)
        return urljoin(self.base_url, filepath_to_uri(name))


class HashedFileSystem(HashedMixin, FileSystem):
    """
    Standard filesystem storage using the hash of the file in the path.
    """
