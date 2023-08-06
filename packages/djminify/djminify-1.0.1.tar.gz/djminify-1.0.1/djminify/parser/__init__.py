# -*- coding: utf-8 -*-

from __future__ import absolute_import

from .. import utils
from .. import settings as conf


def get_default_parser():
    return utils.load_class(conf.DEFAULT_PARSER)()
