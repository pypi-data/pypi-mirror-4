# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import hashlib
import itertools
import io
import os

from django.core.cache import get_cache
from django.contrib.staticfiles import finders
from django.conf import settings

from . import utils
from . import parser
from . import settings as conf
from . import storage

from .compilers import load_compiler_by_type


class Minifier(object):
    def __init__(self, type):
        self.parser = parser.get_default_parser()
        self.storage = storage.get_default_storage()
        self.type = type

        self.create_minify_subdir()

    def minify_js(self, data, regenerate=False):
        elements = self.get_grouped_elements(data, attr="src", selector="script", default="text/javascript")
        output = io.BytesIO()

        for mimetype, files in elements:
            files = (x[1] for x in files)
            compiler = load_compiler_by_type(mimetype)(files, self.storage)
            output.write(compiler.content)

        output.seek(0)
        return output.read()

    def minify_css(self, data, regenerate=False):
        elements = self.get_grouped_elements(data, attr="href", selector="link", default="text/css")
        output = io.BytesIO()

        for mimetype, files in elements:
            files = (x[1] for x in files)
            compiler = load_compiler_by_type(mimetype)(files, self.storage)
            output.write(compiler.content)

        output.seek(0)
        return output.read()

    def get_elements(self, data, attr, selector, default):
        iterator = self.parser.extract_tags(data, attr=attr, selector=selector,
                                                default_type=default)
        for mimetype, file in iterator:
            real_path = finders.find(file)
            if real_path:
                yield mimetype, real_path

    def get_grouped_elements(self, data, attr, selector, default):
        iterator = self.get_elements(data, attr=attr, selector=selector,
                                                        default=default)
        return itertools.groupby(iterator, lambda x: x[0])

    def minify(self, data, regenerate=False):
        enabled = conf.ALWAYS_COMPILE
        if not enabled:
            return data

        cache = get_cache(conf.CACHE_BACKEND)

        hash = self.hash(data)
        cached_key = conf.STANDARD_CACHEKEY.format(hash)
        cached_data = cache.get(cached_key, None)

        if cached_data:
            cache.set(cached_key, cached_data, conf.REBUILD_TIMEOUT)
            return cached_data

        if self.type == "js":
            result = self.minify_js(data, regenerate)
            name = "{0}.js".format(hash)
            template = '<script src="{0}"></script>'
        elif self.type == "css":
            result = self.minify_css(data, regenerate)
            name = "{0}.css".format(hash)
            template = '<link href="{0}" rel="stylesheet" type="text/css" />'
        else:
            raise RuntimeError("unexpected type '{}'".format(self.type))

        path = os.path.join(conf.MINIFY_SUBDIR, name)
        rendered_template = template.format(
                            self.storage.url(path))

        with self.storage.open(path, "wb") as f:
            f.write(result)

        cache.set(cached_key, rendered_template, conf.REBUILD_TIMEOUT)
        return rendered_template

    def hash(self, data):
        return hashlib.md5(data.encode('utf-8')).hexdigest()

    def create_minify_subdir(self):
        path = os.path.join(settings.STATIC_ROOT, conf.MINIFY_SUBDIR)
        if not os.path.exists(settings.STATIC_ROOT):
            os.mkdir(settings.STATIC_ROOT)
        if not os.path.exists(path):
            os.mkdir(path)


class MinifierTemplateMixin(object):
    def render_by_type(self, data, type):
        minifier = Minifier(type)
        return minifier.minify(data)
