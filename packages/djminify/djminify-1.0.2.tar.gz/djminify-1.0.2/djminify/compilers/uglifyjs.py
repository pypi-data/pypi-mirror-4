# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import os.path
import shlex

from subprocess import Popen, PIPE
from django.conf import settings

from . import base
from .. import settings as conf


UGLIFYJS_PATH = getattr(settings,
    "DJANGO_MINIFY_UGLIFYJS_PATH", "/usr/bin/uglifyjs")

UGLIFYJS_PARAMS = getattr(settings,
    "DJANGO_MINIFY_UGLIFYJS_PARAMS", "")


class Minifier(base.BaseMinifier):
    _name = "uglifyjs"
    _type = "text/javascript"

    def run(self):
        if not self._files:
            return b""

        if not os.path.exists(UGLIFYJS_PATH):
            raise RuntimeError("uglify seems not instaled. "
                "Posible fix this with: 'npm install -g uglify-js'")

        cmd = [UGLIFYJS_PATH]
        cmd.extend(self._files)
        cmd.extend(shlex.split(UGLIFYJS_PARAMS))

        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        return stdout
