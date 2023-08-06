# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.db import models
from django.conf import settings
from django import forms
from django.forms.widgets import Widget
from django.utils.safestring import mark_safe
from django.contrib.contenttypes import generic
from django.template.loader import render_to_string
#
from django.utils import simplejson
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
#
import re
import pickle
import base64
import os
from asv_imgs.models import *
from asv_imgs import settings as AIS
#from asv_media.admin import *
from asv_utils.common import Str2Int
#---------------------------------------------------------------
#---------------------------------------------------------------
#def __init__(*args, **kwargs):
#    print 'asv_imgs.admin--init'
class ThumbImg(forms.FileInput):
    def render(self, name, value, attrs=None):
        mu = settings.MEDIA_URL
        if mu[-1] == os.sep:
            mu = mu[:-1]
        ae = [name, value, attrs]
        if value is None:
            rv = super(ThumbImg,self).render(name, value, attrs)
        elif not re.match('{0}/'.format(AIS.ASV_IMGS_STORE_PATH), str(value)):
            rv = super(ThumbImg,self).render(name, value, attrs)
        else:
            rv = render_to_string('asv_imgs__admin__img_preview.html', {
                 'img': value,
                 'size': '{0[0]:d}x{0[1]:d}'.format(AIS.ASV_IMGS_ADMIN_IMG_PREVIEW_SIZE),
                 'MEDIA_URL': mu,
            })
        rv = mark_safe(rv)
        return rv
#---------------------------------------------------------------
#---------------------------------------------------------------
class AsvImgForm(forms.ModelForm):
    class Meta:
        widgets = {
             'img': ThumbImg(),
             #'alt': forms.TextInput(attrs={'size': AIS.ASV_IMGS_ADMIN_ALT_LEN,}),
        }
class AsvImgInline(generic.GenericStackedInline):
    model = AsvImg
    form  = AsvImgForm
    #fields=['img','alt','tags']
    #fields=['img','alt']
    template = 'asv_imgs__admin__stacked.html'
    extra=0
#---------------------------------------------------------------
#---------------------------------------------------------------
#class AsvImgInlineAA(AsvImgInline):
#    fields=['active','img','alt_ru','alt_en','in_new']
#class GalleryTreeFeinAdmin(editor.TreeEditor):
#    inlines = [AsvImgInlineAA, SEOInline]
#    class Media:
#        js = (
#            "/raw/js/admin_gallery_img_positions.js",
#        )
#admin.site.register(GalleryTree, GalleryTreeFeinAdmin)
#---------------------------------------------------------------
#---------------------------------------------------------------
@login_required
def adminRPC_imgsort(request, *args, **kwargs):
    if not request.is_ajax():
        return HttpResponseRedirect('/')
    Result = {}
    if (request.method=='POST') and request.user.is_staff:
        reorder = request.REQUEST.get('reorder',None)
        reorder = simplejson.loads(reorder)
        Mod     = reorder.get('mark',False)
        OrderId = reorder.get('order',[])
        if Mod and OrderId:
            try:
                Mod = base64.b64decode(Mod)
                Mod = pickle.loads(Mod)
            except Exception:
                Mod = False
        if Mod and OrderId:
            Order = []
            id2id = re.compile(r'img_(\d+)')
            for i in OrderId:
                ok = id2id.match(i)
                if ok:
                    Order.append(Str2Int(ok.group(1)))
            #print(Mod,Order)
            Imgs = Mod.objects.filter(id__in=Order)
            #print(Imgs)
            Imgs[0].change_position_order(Order)
            #print(Imgs)
            Result['status'] = 'OK'
        else:
            Result['status'] = 'ERR'
        #del Result['csrfmiddlewaretoken']
    else:
        Result['status'] = 'ERR'
    #---------------
    Result = simplejson.dumps(Result)
    rv = HttpResponse(Result, mimetype='application/json')
    rv['Cache-Control'] = 'no-cache'
    return rv
#---------------------------------------------------------------
#---------------------------------------------------------------
