# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.db.models.signals import *
from django.core.exceptions import *
from django.core.urlresolvers import reverse
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
#from django.template.loader import render_to_string
#from django.utils import simplejson
import os

from mptt.models import MPTTModel
#from taggit.managers import TaggableManager

from asv_utils.common import CleanFileName #, Str2Int
from asv_imgs import settings as AIS
#---------------------------------------------------------------
#---------------------------------------------------------------
class AsvImg(models.Model):
    ImgStorePath = '{0}/asv_imgs'.format(AIS.ASV_IMGS_STORE_PATH)
    def ImgStoreName(instance, filename):
        return '{0}/{1}'.format(instance.ImgStorePath, CleanFileName(filename))
    #----------
    active = models.BooleanField(default=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object=generic.GenericForeignKey('content_type','object_id')
    prio   = models.PositiveIntegerField(default=65000, editable=False)
    #
    img    = models.ImageField(max_length=256, upload_to=ImgStoreName, verbose_name='рисунок')
    alt    = models.CharField(max_length=128, blank=True, verbose_name='подпись')
    #tags   = TaggableManager(blank=True)
    de     = models.DateTimeField(auto_now_add=True)
    lm     = models.DateTimeField(auto_now=True)
    #----------
    def change_position_order(self, ORD=[]):
        '''
        Берем все картинки из данной модели, приаттаченые к одному и тому-же
        content_object, пытаемся упорядочить их в соответствии с порядком ID-ов
        из массива ORD. 
        '''
        def recalc_imgs_prio(iis):
            delta = AIS.ASV_IMGS_DELTA
            if (delta < 10):
                delta = 10
            c = iis.count()
            if not (c > 0):
                return False
            a = 1
            for i in iis:
                t = a * delta
                if (t != i.prio) :
                    i.prio = t
                    i.save()
                a += 1
            return True
        
        CT = self.content_type
        OID= self.object_id
        Imgs = self.__class__.objects.filter(content_type=CT, object_id=OID)
        recalc_imgs_prio(Imgs)
        l = 0
        for i in ORD:
            #print('mainloop: i={}, l={}'.format(i,l))
            if (i == Imgs[l].id):
                #print('NOT need change l={}   i={}, D={}'.format(l,i,Imgs[l].id))
                l += 1
                continue
            # need change position
            #print('need change l={}   i={}, D={}'.format(l,i,Imgs[l].id))
            try:
                cc = self.__class__.objects.get(id=i)
            except:
                #print('not found img with ID={}'.format(i))
                l += 1
                continue
            cc.prio = Imgs[l].prio - 1
            cc.save()
            Imgs = self.__class__.objects.filter(content_type=CT, object_id=OID)
            #print(Imgs)
            #
            l += 1 
        recalc_imgs_prio(Imgs)
        return True

    def get_alt(self, **kwargs):
        rv = False
        try:
            #rv = self.__getattribute__('alt_{}'.format(L))
            rv = self.alt
        except:
            pass
        return rv
    def get_document(self):
        return self.content_object
    def __unicode__(self):
        if (self.id):
            rv = u'<<img {0}>>'.format(self.id)
        else:
            rv = u'<<не_доступно>>'
        if (self.alt):
            rv = u'{0} :: {1}'.format(rv, self.alt)
        else:
            rv = u'{0} :: {1}'.format(rv, '--unnamed--')
        return rv
    def delete(self, using=None):
        try:
            # update Djapian's index, if it is! 
            #AsvImg.indexer.delete(self)
            self.__class__.indexer.delete(self)
        except Exception, e:
            if settings.DEBUG:
                print('asv_imgs::{0}\n{1}'.format(e.__class__.__name__,e))
        try:
            os.remove(self.img.path)
        except:
            pass
        super(AsvImg, self).delete(using)
    def save(self, force_insert=False, force_update=False):
        old = None
        try:
            old = self.__class__.objects.get(pk=self.pk)
        except:
            #print('save. can\'t find old record')
            pass
        if (old):
            oi = old.img
            ni = self.img
            if oi:
                if (((oi and ni) and (oi.path != ni.path)) or ((not ni) and oi)):
                    try:
                        os.remove(oi.path)
                    except:
                        pass
        super(AsvImg, self).save(force_insert, force_update)
        try:
            # update Djapian's index, if it is! 
            #AsvImg.indexer.update()
            self.__class__.indexer.update()
        except Exception, e:
            if settings.DEBUG:
                print('asv_imgs::{0}\n{1}'.format(e.__class__.__name__,e))
    #
    class Meta:
        abstract = True
        ordering = ('content_type', 'prio', 'de')
        verbose_name='рисунок'
        verbose_name_plural='рисунки'
#-------------------------------------------------------------------
#------------------------------------------------------------------- 
