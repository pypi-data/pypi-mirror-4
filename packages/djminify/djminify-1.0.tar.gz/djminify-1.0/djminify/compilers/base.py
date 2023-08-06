
from django.contrib.staticfiles import finders
from ..storage import Storage


class BaseMinifier(object):
    def __init__(self, files, storage):
        self._files = files
        self._storage = storage

    @property
    def content(self):
        if not hasattr(self, "_populated"):
            self._content = self.run()
            self._populated = True

        return self._content

    def run(self):
        raise NotImplementedError

