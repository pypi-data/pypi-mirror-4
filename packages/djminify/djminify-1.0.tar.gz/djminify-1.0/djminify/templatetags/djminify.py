# -*- coding: utf-8 -*-

from django import template
from django.conf import settings

from ..render import MinifierTemplateMixin
register = template.Library()


@register.tag(name="minify")
def minify(parser, token):
    nodelist = parser.parse(('endminify',))
    parser.delete_first_token()

    args = token.split_contents()
    if not len(args) == 2:
        raise template.TemplateSyntaxError(
            "%r tag requires either one argument." % args[0])

    type = parser.compile_filter(args[1])
    return MinifyNode(nodelist, type)


class MinifyNode(MinifierTemplateMixin, template.Node):
    def __init__(self, nodelist, type):
        self.nodelist = nodelist
        self.type = type

    def render(self, context):
        type = self.type.resolve(context)
        data = self.nodelist.render(context)
        return self.render_by_type(data, type)
