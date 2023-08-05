# -*- coding: utf-8 -*-
from __future__ import unicode_literals
#
#from django.core.exceptions import *
#from django.conf import settings
#from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

#from asv_txt.models import *
from asv_utils.common import Str2Int
from asv_txt import settings as ATS

from creoleparser.dialects import create_dialect, creole11_base
from creoleparser.core import Parser as CrParser
from creoleparser import parse_args
from genshi import Markup
import re

Httpx_at_start = re.compile(r'^\s*http.?:\/\/')
Yt_search_key  = re.compile(r'[\?\/\&]v[\/\=]([\w\-]+)')
Yt_validate    = re.compile(r'([\w\-]+)')
#----------------------------------------------------------------
#----------------------------------------------------------------
def GetDefaultAttrs(kwargs):
    rv = []
    X = kwargs.get('class_',kwargs.get('class',kwargs.get('c')))
    if X:
        X.strip()
        X.strip('\'"')
        rv.append('class="{0}"'.format(X))
    X = kwargs.get('id',kwargs.get('id_'))
    if X:
        X.strip()
        X.strip('\'"')
        rv.append('id="{0}"'.format(X))
    return rv
def Yt_validate_key(key):
    k = Yt_validate.search(key)
    if k:
        rv = k.group(1)
    else:
        rv = ''
    return rv
#----------------------------------------------------------------
#----------------------------------------------------------------
def Yt(macro,environ,*args,**kwargs):
    rv = ''
    if len(args) < 1:
        return ''
    key = args[0]
    if Httpx_at_start.match(key):
        k = kwargs.get('v')
        if k:
            key = Yt_validate_key(k)
        else:
            #print('YT key error: str={0}'.format(key))
            return ''
    else:
        key = Yt_validate_key(key)
    rv = render_to_string('yt.html',{ 
        'CODE': key ,
        'S': {
            'w': ATS.ASV_TXT_YT_SIZE[0],
            'h': ATS.ASV_TXT_YT_SIZE[1],
        }
    })
    return Markup(rv)
#----------------------------------------------------------------
#----------------------------------------------------------------
def Img(macro,environ,*args,**kwargs):
    iid = Str2Int(args[0],0)
    if iid < 1:
        return ''
    CT = environ.get('CT',False)
    if not CT:
        return ''
    try:
        rv = CT.imgs.get(active=True, id=iid)
    except Exception:
        return ''
    style = []
    afloat = kwargs.get('float',kwargs.get('f'))
    if afloat and afloat == 'r':
        style.append('float:right')
    elif afloat and afloat == 'l':
        style.append('float:left')
    else:
        afloat = None
    width = kwargs.get('width',kwargs.get('w'))
    if width:
        width=' width="{0}"'.format(Str2Int(width))
    else:
        width=''
    href = kwargs.get('href',kwargs.get('url'))
    #
    if style:
        sstyle = ';'.join(style)+';'
        sstyle = ' style="{0}" '.format(sstyle)
    else:
        sstyle = ''
    if href:
        rv = '<a href="{0}"{1}><img src="{2}" alt="{3}" {4}></a>'.format(href,sstyle,rv.img.url, rv.alt ,width)
    else:
        rv = '<img src="{0}" alt="{1}" {2} {3}>'.format(rv.img.url, rv.alt ,width, sstyle)
    return Markup(rv)
#----------------------------------------------------------------
#----------------------------------------------------------------
def App(macro,environ,*args,**kwargs):
    attrs = GetDefaultAttrs(kwargs)
    body = macro.parsed_body()
    c = macro.arg_string.strip()
    c = c.split()
    if c[0]:
        try:
            href = reverse(c[0], args=c[1:])
        except Exception:
            href='#error'
        attrs.append('href="{0}"'.format(href))
    rv = '<a {0}>{1}</a>'.format(' '.join(attrs),body)
    return Markup(rv)
#----------------------------------------------------------------
#----------------------------------------------------------------
def SimpleTag(macro,environ,*args,**kwargs):
    tag = macro.get('name')
    attrs = GetDefaultAttrs(kwargs)
    body = macro.parsed_body()
    if attrs:
        rv = '<{0} {1}>{2}</{3}>'.format(tag,' '.join(attrs),body,tag)
    else:
        rv = '<{0}>{1}</{2}>'.format(tag,body,tag)
    return Markup(rv)
#----------------------------------------------------------------
#----------------------------------------------------------------
def Columns(macro,environ,*args,**kwargs):
    tag = 'div'
    attrs = GetDefaultAttrs(kwargs)
    cbody = macro.body
    pbody = macro.parsed_body()
    body = '---' # RESULT... тут надо отпарсить body диалектом + тэгом 'C'
    print(macro)
    if attrs:
        rv = '<{0} {1}>{2}</{3}>'.format(tag,' '.join(attrs),body,tag)
    else:
        rv = '<{0}>{1}</{2}>'.format(tag,body,tag)
    return Markup(rv)
#----------------------------------------------------------------
#----------------------------------------------------------------
dia = create_dialect(creole11_base,
    bodied_macros={
            'app': App,
            'div': SimpleTag,
        'columns': Columns,
    },
    non_bodied_macros={
        'img': Img,
        'yt':  Yt,
    },
)
Parse = CrParser(dialect=dia, method='html')
#----------------------------------------------------------------
#----------------------------------------------------------------

