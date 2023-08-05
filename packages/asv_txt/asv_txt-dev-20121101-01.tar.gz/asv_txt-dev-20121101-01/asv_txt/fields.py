# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.core.exceptions import *
from django.core.urlresolvers import reverse
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.forms import CharField, Textarea
from django.forms.util import *
from south.modelsinspector import add_introspection_rules
#---------------------------------------------------------------
#---------------------------------------------------------------
class AsvTxtFormWidget(Textarea):
    def __init__(self, attrs=None):
        default_attrs = {'rel': 'AsvTextarea',}
        if attrs:
            default_attrs.update(attrs)
        super(AsvTxtFormWidget, self).__init__(default_attrs)

    def render(self, name, value, attrs=None):
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        html = '''
        <span>AsvTxt:</span><br>
        <textarea {0}>{1}</textarea>
        '''
        return mark_safe(html.format(
            flatatt(final_attrs),
            conditional_escape(force_unicode(value))
        ))

#---------------------------------------------------------------
#---------------------------------------------------------------
class AsvTxtFormField(CharField):
    widget = AsvTxtFormWidget
    def __init__(self, *args, **kwargs):
        super(AsvTxtFormField, self).__init__(*args, **kwargs)
#---------------------------------------------------------------
#---------------------------------------------------------------
class AsvTxtField(models.TextField):
    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop('model',None)
        super(AsvTxtField, self).__init__(*args, **kwargs)
    def formfield(self, **kwargs):
        defaults = {
                'widget': AsvTxtFormWidget, # forms.Textarea,
            'form_class': AsvTxtFormField,  # forms.TimeField
        }
        defaults.update(kwargs)
        #print(defaults)
        rv = super(AsvTxtField, self).formfield(**defaults)
        rv.widget = AsvTxtFormWidget()
        #e = open('/tmp/qq', 'wb')
        #pickle.dump(rv,e)
        #e.close()
        return rv
    #def to_python(self, value):
    #    rv = super(AsvTxtField, self).to_python(value)
    #    rv = creole2html(rv)
    #    return rv
add_introspection_rules([], ['asv_txt\.fields\.AsvTxtField$'])
#---------------------------------------------------------------
#---------------------------------------------------------------
