# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import io
import os.path

from . import base
from .. import settings as conf


class Minifier(base.BaseMinifier):
    _name = "dummycss"
    _type = "text/css"

    def run(self):
        if not self._files:
            return b""

        with io.BytesIO() as output:
            for file in self._files:
                with io.open(file, "rb") as f:
                    output.write(f.read())

            output.seek(0)
            return output.read()
