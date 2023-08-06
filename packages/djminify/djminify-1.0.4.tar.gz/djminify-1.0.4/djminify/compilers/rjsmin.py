# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import io
from django.conf import settings

try:
    from rjsmin import jsmin
except ImportError:
    raise RuntimeError("rjsmin seems not instaled. "
                "Posible fix this with: 'pip install rjsmin'")

from . import base
from .. import settings as conf


class Minifier(base.BaseMinifier):
    _name = "rjsmin"
    _type = "text/javascript"

    def run(self):
        if not self._files:
            return b""

        with io.BytesIO() as output:
            for file in self._files:
                with io.open(file, "rt") as f:
                    minified_out = jsmin(f.read())
                    output.write(minified_out.encode('utf-8'))

            output.seek(0)
            return output.read()
