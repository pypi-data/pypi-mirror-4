# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django import template
from django.utils.safestring import mark_safe
from asv_txt.markup import Parse
#
register = template.Library()
#---------------------------------------------------------------
#---------------------------------------------------------------
class render_txtNode(template.Node):
    def __init__(self, source_var, context_name=None):
        self.ct_var = template.Variable('CT')
        self.source_var = source_var
        self.context_name = context_name
    def render(self, context):
        try:
            ct = self.ct_var.resolve(context)
        except template.VariableDoesNotExist:
            ct = None
        try:
            source = self.source_var.resolve(context)
        except template.VariableDoesNotExist:
            if raise_errors:
                raise template.VariableDoesNotExist("Variable '%s' does not exist." %
                        self.source_var)
            return self.bail_out(context)
        #
        if (source):
            rv = Parse(source, environ={'CT': ct})
        else:
            rv = ''
        if self.context_name is None:
            return mark_safe(rv)
        else:
            context[self.context_name] = mark_safe(rv)
            return ''
@register.tag
def render_txt(parser, token):
    args = token.split_contents()
    tag = args[0]
    # Check to see if we're setting to a context variable.
    if len(args) >= 4 and args[-2] == 'as':
        context_name = args[-1]
        args = args[:-2]
    else:
        context_name = None
    return render_txtNode(parser.compile_filter(args[1]), context_name)
#---------------------------------------------------------------
#---------------------------------------------------------------
class render_ct_txtNode(template.Node):
    def __init__(self, source_var, context_name=None):
        self.source_var = source_var
        self.context_name = context_name
    def render(self, context):
        try:
            source = self.source_var.resolve(context)
        except template.VariableDoesNotExist:
            if raise_errors:
                raise template.VariableDoesNotExist("Variable '%s' does not exist." %
                        self.source_var)
            return self.bail_out(context)
        if not source:
            if raise_errors:
                raise template.TemplateSyntaxError(
                    "Variable '%s' is an invalid source." % self.source_var
                )
            return self.bail_out(context)
        #
        try:
            txt = source.txt.all()
            txt = txt[0]
        except:
            txt = None
        if (txt):
            rv = Parse(txt.get_txt(), environ={'CT':source})
        else:
            rv = ''
        if self.context_name is None:
            return mark_safe(rv)
        else:
            context[self.context_name] = mark_safe(rv)
            return ''
@register.tag
def render_ct_txt(parser, token):
    args = token.split_contents()
    tag = args[0]
    # Check to see if we're setting to a context variable.
    if len(args) >= 4 and args[-2] == 'as':
        context_name = args[-1]
        args = args[:-2]
    else:
        context_name = None
    return render_ct_txtNode(parser.compile_filter(args[1]), context_name)
#---------------------------------------------------------------
#---------------------------------------------------------------
