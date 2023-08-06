# -*- coding: utf-8 -*-

from django.conf import settings
import os, os.path

DEFAULT_MINIFIERS = {
    "text/javascript": "djminify.compilers.uglifyjs",
    "text/less": "djminify.compilers.lessc",
    "text/css": "djminify.compilers.dummycss",
}

REGENERATE_CACHEKEY = getattr(settings,
    'DJANGO_MINIFY_REGENERATE_KEY', 'djminify.regenerate')

STANDARD_CACHEKEY = getattr(settings,
    'DJANGO_MINIFY_STANDARD_KEY', 'djminify.block.{0}')

ALWAYS_COMPILE = getattr(settings,
    "DJANGO_MINIFY_ALWAY_COMPILE", not settings.DEBUG)

CACHE_BACKEND = getattr(settings,
    "DJANGO_MINIFY_CACHE_BACKEND", "default")

REBUILD_TIMEOUT = getattr(settings,
    "DJANGO_MINIFY_REBUILD_TIMEOUT", 60*60*24)

DEFAULT_PARSER = getattr(settings,
    "DJANGO_MINIFY_DEFAULT_PARSER", "djminify.parser.lxml.LxmlParser")

DEFAULT_STORAGE = getattr(settings,
    "DJANGO_MINIFY_DEFAULT_STORAGE", "djminify.storage.Storage")

MINIFY_SUBDIR = getattr(settings,
    "DJANGO_MINIFY_STATIC_SUBDIR", "minify")

if hasattr(settings, "DJANGO_MINIFY_DEFAULT_COMPILERS"):
    DEFAULT_MINIFIERS.update(settings.DJANGO_MINIFY_MIFIERS)


