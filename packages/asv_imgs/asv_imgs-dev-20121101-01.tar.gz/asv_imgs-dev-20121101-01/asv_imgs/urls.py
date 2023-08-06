# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls.defaults import *
from asv_imgs.admin import adminRPC_imgsort
#from django.views.static import serve
#from asv_imgs import settings as AIS

#def __init__(*args, **kwargs):
#    print 'asv_imgs.urls--init'
urlpatterns = patterns('',
    url(r'^imgsort/$', adminRPC_imgsort, name='asv_imgs__adminrpc__imgsort'),
    #url(r'^media/?$', serve, {'document_root':AIS.ASV_IMGS_MEDIA_ROOT}, name='asv_imgs__media_url'),
    #url(r'^media/(?P<path>.*)$', serve, {'document_root':AIS.ASV_IMGS_MEDIA_ROOT}, name='asv_imgs__media'),
)


