from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import gzip
import io
import mimetypes
import os

from boto.exception import S3ResponseError
from boto.s3.connection import S3Connection, SubdomainCallingFormat
from boto.s3.key import Key
from dateutil import parser, tz

from .base import Storage
from .exceptions import SuspiciousOperation
from .hashed import HashedMixin
from .utils.encoding import force_text, force_bytes


class S3File(object):
    """
    The default file object used by the S3 backend.

    This file implements file streaming using boto's multipart
    uploading functionality. The file can be opened in read or
    write mode.

    This class extends Django's File class. However, the contained
    data is only the data contained in the current buffer. So you
    should not access the contained file object directly. You should
    access the data via this class.

    Warning: This file *must* be closed using the close() method in
    order to properly write the file to S3. Be sure to close the file
    in your application.
    """

    # TODO: Read/Write (rw) mode may be a bit undefined at the moment.
    # TODO: Rewrite to use the BufferedIO streams in the Python 2.6 io module.

    def __init__(self, name, mode, storage, buffer_size=5242880):
        self._storage = storage
        self.name = name[len(self._storage.location):].lstrip("/")
        self._mode = mode
        self.key = storage.bucket.get_key(self._storage._encode_name(name))

        if not self.key and "w" in mode:
            self.key = storage.bucket.new_key(storage._encode_name(name))

        self._is_dirty = False
        self._cached_file = None
        self._multipart = None

        # 5 MB is the minimum part size (if there is more than one part).
        # Amazon allows up to 10,000 parts.  The default supports uploads
        # up to roughly 50 GB.  Increase the part size to accommodate
        # for files larger than this.
        self._write_buffer_size = buffer_size
        self._write_counter = 0

    def __str__(self):
        return force_text(self.name or "")

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self or "None")

    def __bool__(self):
        return bool(self._file)

    def __nonzero__(self):  # Python 2 compatibility
        return type(self).__bool__(self)

    def __len__(self):
        return self.size

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.close()

    def __iter__(self):
        # Iterate over this file-like object by newlines
        for line in self.xreadlines():
            yield line

    @property
    def _file(self):
        if self._cached_file is None:
            self._cached_file = io.Bytes()
            if 'r' in self._mode:
                self._is_dirty = False
                self.key.get_contents_to_file(self._cached_file)
                self._cached_file.seek(0)
            if self._storage.gzip and self.key.content_encoding == "gzip":
                self._cached_file = gzip.GzipFile(
                                        mode=self._mode,
                                        fileobj=self._cached_file,
                                    )
        return self._cached_file

    @_file.setter
    def _set_file(self, value):
        self._cached_file = value

    @property
    def _buffer_file_size(self):
        pos = self.file.tell()
        self.file.seek(0, os.SEEK_END)
        length = self.file.tell()
        self.file.seek(pos)
        return length

    def _flush_write_buffer(self):
        """
        Flushes the write buffer.
        """
        if self._buffer_file_size:
            self._write_counter += 1
            self.file.seek(0)
            self._multipart.upload_part_from_file(
                self.file,
                self._write_counter,
                headers=self._storage.headers
            )
            self.file.close()
            self.file = None

    @property
    def closed(self):
        return not self._file or self._file.closed

    @property
    def encoding(self):
        return self._file.encoding

    @property
    def size(self):
        return self.key.size

    def seek(self, *args, **kwargs):
        return self._file.seek(*args, **kwargs)

    def tell(self, *args, **kwargs):
        return self._file.tell(*args, **kwargs)

    def truncate(self, *args, **kwargs):
        return self._file.truncate(*args, **kwargs)

    def read(self, *args, **kwargs):
        if "r" not in self._mode:
            raise AttributeError("File was not opened in read mode.")
        return self._file.read(*args, **kwargs)

    def readline(self, *args, **kwargs):
        if "r" not in self._mode:
            raise AttributeError("File was not opened in read mode.")
        return self._file.readline(*args, **kwargs)

    def readlines(self, *args, **kwargs):
        if "r" not in self._mode:
            raise AttributeError("File was not opened in read mode.")
        return self._file.readlines(*args, **kwargs)

    def xreadlines(self, *args, **kwargs):
        if "r" not in self._mode:
            raise AttributeError("File was not opened in read mode.")
        return self._file.xreadlines(*args, **kwargs)

    def write(self, *args, **kwargs):
        if "w" not in self._mode:
            raise AttributeError("File was not opened in write mode.")

        self._is_dirty = True

        if self._multipart is None:
            provider = self.key.bucket.connection.provider
            upload_headers = {
                provider.acl_header: self._storage.acl
            }
            upload_headers.update(self._storage.headers)
            self._multipart = self._storage.bucket.initiate_multipart_upload(
                self.key.name,
                headers=upload_headers,
                reduced_redundancy=self._storage.reduced_redundancy
            )

        if self._write_buffer_size <= self._buffer_file_size:
            self._flush_write_buffer()

        return self._file.write(*args, **kwargs)

    def writelines(self, *args, **kwargs):
        return self._file.writelines(*args, **kwargs)

    def flush(self, *args, **kwargs):
        return self._file.flush(*args, **kwargs)

    def close(self):  # #
        if self._is_dirty:
            self._flush_write_buffer()
            self._multipart.complete_upload()
        else:
            if not self._multipart is None:
                self._multipart.cancel_upload()

        self.key.close()


def safe_join(base, *paths):
    """
    A version of stockpile.utils._os.safe_join for S3 paths.

    Joins one or more path components to the base path component
    intelligently. Returns a normalized version of the final path.

    The final path must be located inside of the base path component
    (otherwise a ValueError is raised).

    Paths outside the base path indicate a possible security
    sensitive operation.
    """
    from urlparse import urljoin
    base_path = force_text(base)
    base_path = base_path.rstrip("/")
    paths = [force_text(p) for p in paths]

    final_path = base_path
    for path in paths:
        final_path = urljoin(final_path.rstrip("/") + "/", path.rstrip("/"))

    # Ensure final_path starts with base_path and that the next character after
    # the final path is '/' (or nothing, in which case final_path must be
    # equal to base_path).
    base_path_len = len(base_path)
    if (not final_path.startswith(base_path) or
            final_path[base_path_len:base_path_len + 1] not in ("", "/")):
        raise ValueError("the joined path is located outside of the base path"
                         " component")

    return final_path.lstrip("/")


class S3(Storage):
    """
    Amazon Simple Storage Service using Boto

    This storage backend supports opening files in read or write
    mode and supports streaming(buffering) data in chunks to S3
    when writing.
    """

    connection_class = S3Connection
    connection_response_error = S3ResponseError

    def __init__(self, access_key=None, secret_key=None, **kwargs):
        self.acl = kwargs.pop("acl", "public-read")
        self.auto_create_bucket = kwargs.pop("auto_create_bucket", False)
        self.bucket_acl = kwargs.pop("bucket_acl", "public-read")
        self.bucket_name = kwargs.pop("bucket", None)
        self.headers = kwargs.pop("headers", {})
        self.preload_metadata = kwargs.pop("preload_metadata", False)
        self.gzip = kwargs.pop("gzip", False)
        self.gzip_content_types = kwargs.pop("gzip_content_types",
            set([
                "text/css",
                "application/javascript",
                "application/x-javascript",
            ]),
        )
        self.querystring_auth = kwargs.pop("querystring_auth", False)
        self.querystring_expire = kwargs.pop("querystring_expire", 3600)
        self.reduced_redundancy = kwargs.pop("reduced_redundancy", False)
        self.encryption = kwargs.pop("encryption", False)
        self.custom_domain = kwargs.pop("custom_domain", None)
        self.secure_urls = kwargs.pop("secure_urls", False)
        self.url_protocol = kwargs.pop("url_protocol",
            "http" if not self.secure_urls else "https",
        )
        self.location = kwargs.pop("location", "").lstrip("/")
        self.file_name_charset = kwargs.pop("file_name_charset", "utf-8")
        self.calling_format = kwargs.pop("calling_format",
            SubdomainCallingFormat(),
        )
        self.file_overwrite = kwargs.pop("file_overwrite", True)

        self.connection = self.connection_class(
                                access_key,
                                secret_key,
                                calling_format=self.calling_format,
                            )

        self._entries = {}

        super(S3, self).__init__(**kwargs)

    @property
    def bucket(self):
        """
        Get the current bucket. If there is no current bucket object
        create it.
        """
        if not hasattr(self, "_bucket"):
            self._bucket = self._get_or_create_bucket(self.bucket_name)
        return self._bucket

    @property
    def entries(self):
        """
        Get the locally cached files for the bucket.
        """
        if self.preload_metadata and not self._entries:
            self._entries = dict((self._decode_name(entry.key), entry)
                                for entry in self.bucket.list())
        return self._entries

    def _get_or_create_bucket(self, name):
        """
        Retrieves a bucket if it exists, otherwise creates it.
        """
        try:
            return self.connection.get_bucket(name,
                        validate=self.auto_create_bucket,
                    )
        except self.connection_response_error:
            if self.auto_create_bucket:
                bucket = self.connection.create_bucket(name)
                bucket.set_acl(self.bucket_acl)
                return bucket

            raise RuntimeError(
                "Bucket specified by bucket_name does not exist. Buckets can "
                "be automatically created by setting auto_create_bucket=True"
            )

    def _clean_name(self, name):
        """
        Cleans the name so that Windows style paths work
        """
        # Useful for windows' paths
        return os.path.normpath(name).replace("\\", "/")

    def _normalize_name(self, name):
        """
        Normalizes the name so that paths like /ignored/path/../something.txt
        work. We check to make sure that the path pointed to is not outside
        the directory specified by the LOCATION setting.
        """
        try:
            return safe_join(self.location, name)
        except ValueError:
            raise SuspiciousOperation(
                "Attempted access to '%s' denied." % name,
            )

    def _encode_name(self, name):
        return force_bytes(name, encoding=self.file_name_charset)

    def _decode_name(self, name):
        return force_text(name, encoding=self.file_name_charset)

    def _compress_content(self, content):
        """
        Gzip a given string content.
        """
        zbuf = io.BytesIO()
        zfile = gzip.GzipFile(mode="wb", compresslevel=9, fileobj=zbuf)

        try:
            zfile.write(content.read())
        finally:
            zfile.close()

        content.file = zbuf
        content.seek(0)

        return content

    def _open(self, name, mode="rb"):
        name = self._normalize_name(self._clean_name(name))
        f = S3File(name, mode, self)

        if not f.key:
            raise IOError("File does not exist: %s" % name)

        return f

    def _save(self, name, content):
        cleaned_name = self._clean_name(name)
        name = self._normalize_name(cleaned_name)
        headers = self.headers.copy()
        content_type = getattr(content, "content_type",
            mimetypes.guess_type(name)[0] or Key.DefaultContentType)

        # setting the content_type in the key object is not enough.
        self.headers.update({"Content-Type": content_type})

        if self.gzip and content_type in self.gzip_content_types:
            content = self._compress_content(content)
            headers.update({"Content-Encoding": "gzip"})

        content.name = cleaned_name
        encoded_name = self._encode_name(name)
        key = self.bucket.get_key(encoded_name)

        if not key:
            key = self.bucket.new_key(encoded_name)

        if self.preload_metadata:
            self._entries[encoded_name] = key

        key.set_metadata("Content-Type", content_type)

        # only pass backwards incompatible arguments if they vary from the
        #   default
        kwargs = {}

        if self.encryption:
            kwargs['encrypt_key'] = self.encryption

        key.set_contents_from_file(content,
            headers=headers,
            policy=self.acl,
            reduced_redundancy=self.reduced_redundancy,
            rewind=True,
            **kwargs
        )

        return cleaned_name

    def delete(self, name):
        name = self._normalize_name(self._clean_name(name))
        self.bucket.delete_key(self._encode_name(name))

    def exists(self, name):
        name = self._normalize_name(self._clean_name(name))

        if self.entries:
            return name in self.entries

        k = self.bucket.new_key(self._encode_name(name))

        return k.exists()

    def listdir(self, name):
        name = self._normalize_name(self._clean_name(name))

        # for the bucket.list and logic below name needs to end in /
        # But for the root path "" we leave it as an empty string
        if name:
            name += "/"

        dirlist = self.bucket.list(self._encode_name(name))

        files = []
        dirs = set()

        base_parts = name.split("/")[:-1]
        for item in dirlist:
            parts = item.name.split("/")
            parts = parts[len(base_parts):]
            if len(parts) == 1:
                # File
                files.append(parts[0])
            elif len(parts) > 1:
                # Directory
                dirs.add(parts[0])

        return list(dirs), files

    def size(self, name):
        name = self._normalize_name(self._clean_name(name))

        if self.entries:
            entry = self.entries.get(name)
            if entry:
                return entry.size
            return 0

        return self.bucket.get_key(self._encode_name(name)).size

    def modified_time(self, name):
        name = self._normalize_name(self._clean_name(name))
        entry = self.entries.get(name)

        # only call self.bucket.get_key() if the key is not found
        # in the preloaded metadata.
        if entry is None:
            entry = self.bucket.get_key(self._encode_name(name))

        # convert to string to date
        last_modified_date = parser.parse(entry.last_modified)

        # if the date has no timzone, assume UTC
        if last_modified_date.tzinfo == None:
            last_modified_date = last_modified_date.replace(tzinfo=tz.tzutc())

        return last_modified_date

    def get_available_name(self, name):
        """
        Overwrite existing file with the same name.
        """
        if self.file_overwrite:
            name = self._clean_name(name)
            return name

        return super(S3, self).get_available_name(name)

    def url(self, name):
        name = self._normalize_name(self._clean_name(name))

        if self.custom_domain:
            return "%s://%s/%s" % (self.url_protocol, self.custom_domain, name)

        return self.connection.generate_url(
                    self.querystring_expire,
                    method="GET",
                    bucket=self.bucket.name,
                    key=self._encode_name(name),
                    query_auth=self.querystring_auth,
                    force_http=not self.secure_urls,
                )


class HashedS3(HashedMixin, S3):
    """
    S3 storage using the hash of the file in the path.
    """
