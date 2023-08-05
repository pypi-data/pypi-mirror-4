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
def path2filename(p):
    n = p.split('/')
    try:
        rv = n[-1]
    except Exception:
        rv = ''
    return rv
#---------------------------------------------------------------
#---------------------------------------------------------------
class filenameNode(template.Node):
    def __init__(self, obbj, context_name=None):
        self.obbj = obbj
        self.context_name = context_name
    def render(self, context):
        M = context[self.obbj]
        fp = '{0}'.format(M.field.value())
        rv = path2filename(fp)
        if self.context_name is None:
            return rv
        else:
            context[self.context_name] = rv
            return ''
@register.tag
def filename(parser, token):
    args = token.split_contents()
    #tag = args[0]
    # Check to see if we're setting to a context variable.
    if len(args) >= 4 and args[-2] == 'as':
        context_name = args[-1]
        args = args[:-2]
    else:
        context_name = None
    #return asv_pickleNode(parser.compile_filter(args[1]), context_name)
    return filenameNode(args[1], context_name)
#---------------------------------------------------------------
#---------------------------------------------------------------
class FF(object):
    files = []
    def __init__(self, files):
        self.files = files
    @property
    def is_empty(self):
        try:
            n = self.files.count()
        except Exception:
            n = len(self.files)
        if n > 0:
            rv = False
        else:
            rv = True
        return rv
    @property
    def has_files(self):
        return not self.is_empty
    @property
    def as_ul(self):
        if self.is_empty:
            return ''
        rv = ''
        tm = '<li><a href="{0}" title="{1}">{2}</a></li>'
        for i in self.files:
            fn = '{0}'.format(i.file)
            t = i.title
            if not t:
                t = path2filename(fn)
            rv+= tm.format(i.file.url,t,t)
        return mark_safe(rv)
    def __unicode__(self):
        q = []
        for i in self.files:
            a = ''.format(i.file)
            q.append(a.split('/')[-1])
        return smart_unicode(' '.join(q))

class files_ctNode(template.Node):
    raise_errors = True
    def __init__(self, source_var, context_name=None):
        self.source_var = source_var
        self.context_name = context_name
    def render(self, context):
        try:
            source = self.source_var.resolve(context)
        except template.VariableDoesNotExist:
            if self.raise_errors:
                raise template.VariableDoesNotExist("Variable '%s' does not exist." %
                        self.source_var)
            return self.bail_out(context)
        if not source:
            if self.raise_errors:
                raise template.TemplateSyntaxError(
                        "Variable '%s' is an invalid source." % self.source_var
                )
            return self.bail_out(context)
        #
        try:
            files = source.files.filter(active=True)
        except Exception:
            files = []
        rv = FF(files)
        if self.context_name is None:
            return rv
        else:
            context[self.context_name] = rv
            return ''
@register.tag
def files_ct(parser, token):
    args = token.split_contents()
    if len(args) >= 4 and args[-2] == 'as':
        context_name = args[-1]
        args = args[:-2]
    else:
        context_name = None
    return files_ctNode(parser.compile_filter(args[1]), context_name)
#---------------------------------------------------------------
#---------------------------------------------------------------
