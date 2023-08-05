# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import template
import pickle
import base64
from django.utils.encoding import smart_unicode
from django.utils.safestring import mark_safe

register = template.Library()

#---------------------------------------------------------------
#---------------------------------------------------------------
class asv__url_pickleNode(template.Node):
    def __init__(self, obbj, context_name=None):
        self.obbj = obbj
        self.context_name = context_name
    def render(self, context):
        M = context[self.obbj]
        MM = M.formset.model
        rv = pickle.dumps(MM,pickle.HIGHEST_PROTOCOL)
        rv = base64.b64encode(rv)
        if self.context_name is None:
            return rv
        else:
            context[self.context_name] = rv
            return ''
@register.tag
def asv__url_pickle(parser, token):
    args = token.split_contents()
    tag = args[0]
    # Check to see if we're setting to a context variable.
    if len(args) >= 4 and args[-2] == 'as':
        context_name = args[-1]
        args = args[:-2]
    else:
        context_name = None
    #return asv_pickleNode(parser.compile_filter(args[1]), context_name)
    return asv__url_pickleNode(args[1], context_name)
#---------------------------------------------------------------
#---------------------------------------------------------------
