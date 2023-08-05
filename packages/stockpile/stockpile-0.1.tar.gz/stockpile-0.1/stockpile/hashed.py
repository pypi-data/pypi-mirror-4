import hashlib
import os


class HashedMixin(object):

    def __init__(self, hash_algorithm=None, **kwargs):
        self.hash_algorithm = hash_algorithm

        super(HashedMixin, self).__init__(**kwargs)

    def save(self, name, content, *args, **kwargs):
        if not self.hash_algorithm is None:
            hasher = getattr(hashlib, self.hash_algorithm)
            hashed = hasher()

            for chunk in self._chunks(content):
                hashed.update(chunk)

            digest = hashed.hexdigest()
            parts = list(digest[:5]) + [digest, name]
            name = os.path.join(*parts)

        return super(HashedMixin, self).save(name, content, *args, **kwargs)
