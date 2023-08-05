# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.db.models.signals import *
#from django.core.files.storage import FileSystemStorage
from django.core.exceptions import *
from django.core.urlresolvers import reverse
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
#from django.template.loader import render_to_string
#from django.utils import simplejson
#from pytils.translit import translify , slugify
#import os

from asv_txt.fields import AsvTxtField
#---------------------------------------------------------------
#---------------------------------------------------------------
class AsvTxt(models.Model):
    #----------
    active = models.BooleanField(default=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object=generic.GenericForeignKey('content_type','object_id')
    #prio   = models.PositiveIntegerField(default=65000, editable=False)
    #
    lang   = models.CharField(max_length=2, default='ru', editable=False)
    txt    = AsvTxtField(blank=True, default='')
    txthash= models.CharField(max_length=255, blank=True, editable=False)
    #tags   = TaggableManager(blank=True)
    de     = models.DateTimeField(auto_now_add=True)
    lm     = models.DateTimeField(auto_now=True)
    #----------
    def __unicode__(self):
        if (self.id):
            rv = u'[txt=%d]'%(self.id)
        else:
            rv = u'[не_доступно]'
        #if (self.alt):
        #    rv = u'%s :: %s'%(rv,self.alt)
        #else:
        #    rv = u'%s :: %s'%(rv,'--unnamed--')
        return rv
    def get_txt(self):
        return self.txt
    def get_document(self):
        return self.content_object
    def delete(self, using=None):
        try:
            # update Djapian's index, if it is!
            #AsvTxt.indexer.delete(self)
            self.__class__.indexer.delete(self)
        except Exception, e:
            if settings.DEBUG:
                print('asv_txt::{0}\n{1}'.format(e.__class__.__name__,e))
        super(AsvTxt, self).delete(using)
    def save(self, force_insert=False, force_update=False):
        super(AsvTxt, self).save(force_insert, force_update)
        try:
            # update Djapian's index, if it is!
            #AsvTxt.indexer.update()
            self.__class__.indexer.update()
        except Exception, e:
            if settings.DEBUG:
                print('asv_txt::{0}\n{1}'.format(e.__class__.__name__,e))
    #
    class Meta:
        abstract = True
        ordering = ('content_type', 'lang', 'de')
        verbose_name='текст'
        verbose_name_plural='тексты'
#def GalleryImg_post_save(instance,**kwargs):
#    return True
#post_save.connect(GalleryImg_post_save, sender=GalleryImg)
#------------------------------------------------------------------- 
#------------------------------------------------------------------- 
