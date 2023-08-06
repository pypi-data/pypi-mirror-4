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


LESSC_PATH = getattr(settings,
    "DJANGO_MINIFY_LESSC_PATH", "/usr/bin/lessc")

LESSC_PARAMS = getattr(settings,
    "DJANGO_MINIFY_LESSC_PARAMS", "--yui-compress")


class Minifier(base.BaseMinifier):
    _name = "lessc"
    _type = "text/less"

    def get_less_for_file(self, path):
        tmpdir = tempfile.mkdtemp(prefix="lessc")
        outfile = os.path.join(tmpdir, "style.css")

        cmd = "{0} {1} {2} {3}".format(
            LESSC_PATH, LESSC_PARAMS, path, outfile)

        p = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE)
        p.wait()

        if not os.path.exists(outfile):
            raise RuntimeError("unexpected error on compile less")

        with io.open(outfile, "rb") as f:
            stdout = f.read()

        shutil.rmtree(tmpdir)
        return stdout

    def run(self):
        if not self._files:
            return b""

        if not os.path.exists(LESSC_PATH):
            raise RuntimeError("lessc seems not instaled. "
                "Posible fix this with: 'npm install -g less'")

        with io.BytesIO() as output:
            for file in self._files:
                output.write(self.get_less_for_file(file))

            output.seek(0)
            return output.read()
