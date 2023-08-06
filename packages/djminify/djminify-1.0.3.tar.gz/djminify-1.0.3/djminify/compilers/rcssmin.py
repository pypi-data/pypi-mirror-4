# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import io
from django.conf import settings

try:
    from rcssmin import cssmin
except ImportError:
    raise RuntimeError("rcssmin seems not instaled. "
                "Posible fix this with: 'pip install rcssmin'")

from . import base
from .. import settings as conf


class Minifier(base.BaseMinifier):
    _name = "rcssmin"
    _type = "text/css"

    def run(self):
        if not self._files:
            return b""

        with io.BytesIO() as output:
            for file in self._files:
                with io.open(file, "rt") as f:
                    minified_out = cssmin(f.read())
                    output.write(minified_out.encode('utf-8'))

            output.seek(0)
            return output.read()
