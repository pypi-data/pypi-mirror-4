# -*- coding: utf-8 -*-

from jinja2 import nodes
from jinja2.ext import Extension
from jinja2.exceptions import TemplateSyntaxError

from ..render import MinifierTemplateMixin


class MinifyExtension(MinifierTemplateMixin, Extension):
    tags = set(['minify'])

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        firstarg = parser.parse_expression()

        if firstarg.value not in ["js", "css"]:
            raise TemplateSyntaxError('minify argument may be one of: "js" or "css"', lineno)

        body = parser.parse_statements(['name:endminify'], drop_needle=True)
        return nodes.CallBlock(self.call_method('_minify', [firstarg]), [], [],
                                                    body).set_lineno(lineno)

    def _minify(self, type, caller):
        return self.render_by_type(caller(), type)
