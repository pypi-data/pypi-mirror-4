# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django.core.exceptions import ImproperlyConfigured

try:
    from lxml import html as lxhtml
except ImportError:
    raise ImproperlyConfigured("lxml and cssselect package not instaled")

from . import base


class LxmlParser(base.Parser):
    def extract_tags(self, data, attr, selector, default_type):
        fragment = lxhtml.fromstring(data)

        for node in fragment.cssselect(selector):
            attrdata = dict(node.items())

            if attr not in attrdata:
                continue

            _type = attrdata.get('type', default_type)
            _src = attrdata[attr]

            yield _type, self.translate_path(_src)
