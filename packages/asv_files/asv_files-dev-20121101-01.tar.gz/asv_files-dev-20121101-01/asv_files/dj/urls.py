# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from asv_files.dj.admin import adminRPC_filesort
from asv_files.dj.views import *
try:
    from django.conf.urls import patterns, url
except ImportError:
    from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^asv_files/filesort/$', adminRPC_filesort, name='adminrpc__filesort'),
    url(r'^asv_files/formfield_config/$', FormFieldConfig.as_view(), name='formfield_config'),
    url(r'^asv_files/formfield_config/(?P<FID>.*)/$', FormFieldConfig.as_view()),
    url(r'^asv_files/formfield_file_upload/(?P<FID>.*)/$', FileUpload.as_view(), name='formfield_file_upload'),
)



