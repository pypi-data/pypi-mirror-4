from django import template
from django.template.base import TemplateSyntaxError, TemplateDoesNotExist, Variable, FilterExpression
from django.template.base import Library, Node, TextNode
from django.template.defaulttags import token_kwargs
from ..utils import canjs_urls

register = template.Library()

allowed_libraries = ("dojo", "jquery", "mootools", "yui", "zepto")
allowed_extras = (
    "jquery", "csrf",
    "construct.proxy", "construct.super", "control.plugin",
    "observe.attributes", "observe.backup", "observe.delegate",
    "observe.setter", "observe.validations"
)

class CanJSNode(template.Node):
    def __init__(self, urls):
        self.urls = urls

    def render(self, context):
        return "\n".join(["<script type='text/javascript' src='%s'></script>" % u for u in self.urls])

@register.tag(name="canjs")
def canjs(parser, token):
    bits = token.split_contents()
    if len(bits) > 1:
        kwargs = token_kwargs(bits[1:], parser, support_legacy=False)
        for k,v in kwargs.iteritems():
            if isinstance(v, FilterExpression):
                v = str(v.var)
                if k == "extras":
                    v = v.split(",")
                kwargs[k] = v
        urls = canjs_urls(**kwargs)
    else:
        urls = canjs_urls()
    return CanJSNode(urls=urls)
