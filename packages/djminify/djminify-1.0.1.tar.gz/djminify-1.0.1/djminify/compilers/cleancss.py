# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import io
import os.path
import shlex
import shutil
import tempfile

from subprocess import Popen, PIPE
from django.conf import settings

from . import base
from .. import settings as conf


CLEANCSS_PATH = getattr(settings,
    "DJANGO_MINIFY_CLEANCSS_PATH", "/usr/bin/cleancss")

CLEANCSS_PARAMS = getattr(settings,
    "DJANGO_MINIFY_CLEANCSS_PARAMS", "-e")


class Minifier(base.BaseMinifier):
    _name = "cleancss"
    _type = "text/css"

    def get_css_for_file(self, path):
        cmd = "{0} {1} {2}".format(
            CLEANCSS_PATH, CLEANCSS_PARAMS, path)

        p = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        return out

    def run(self):
        if not self._files:
            return b""

        if not os.path.exists(CLEANCSS_PATH):
            raise RuntimeError("lessc seems not instaled. "
                "Posible fix this with: 'npm install -g clean-css'")

        with io.BytesIO() as output:
            for file in self._files:
                output.write(self.get_css_for_file(file))

            output.seek(0)
            return output.read()
