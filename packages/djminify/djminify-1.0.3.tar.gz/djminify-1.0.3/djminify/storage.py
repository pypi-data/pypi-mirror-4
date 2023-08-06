# -*- coding: utf-8 -*-

from django.core.files.storage import FileSystemStorage, get_storage_class
from django.conf import settings

from . import utils
from . import settings as conf


def get_default_storage(*args, **kwargs):
    return utils.load_class(conf.DEFAULT_STORAGE)(*args, **kwargs)


class Storage(FileSystemStorage):
    def __init__(self, location=None, base_url=None, *args, **kwargs):
        if location is None:
            location = settings.STATIC_ROOT
        if base_url is None:
            base_url = settings.STATIC_URL

        super(Storage, self).__init__(location, base_url,
                                                    *args, **kwargs)

