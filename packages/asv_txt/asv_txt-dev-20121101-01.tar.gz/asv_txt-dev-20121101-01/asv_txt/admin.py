from __future__ import unicode_literals
    
from django.contrib import admin
from django.contrib.contenttypes import generic


from asv_txt.models import *
#---------------------------------------------------------------
#---------------------------------------------------------------
class AsvTxtInline(generic.GenericStackedInline):
    model = AsvTxt
    extra=1
    max_num=1
#---------------------------------------------------------------
#---------------------------------------------------------------
