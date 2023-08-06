# -*- coding: utf-8 -*-

from django.contrib.staticfiles import finders
from .storage import Storage

class Finder(finders.BaseStorageFinder):
    storage = Storage

    def list(self, ignore_patterns):
        return []
