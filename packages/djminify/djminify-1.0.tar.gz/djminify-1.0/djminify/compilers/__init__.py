# -*- coding: utf-8 -*-

from .. import utils, settings as conf

def load_compiler_by_type(_type):
    if _type not in conf.DEFAULT_MINIFIERS:
        raise RuntimeError("'{0}' type does not have minifier".format(_type))

    cls_path = conf.DEFAULT_MINIFIERS[_type]
    return utils.load_class("{0}.Minifier".format(cls_path))
