# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django import forms
from django.contrib.contenttypes import generic
from django.utils import simplejson
from django.http import  HttpResponseRedirect
from django.contrib.auth.decorators import login_required
import re
import pickle
import base64
from asv_utils.common import Str2Int
from asv_utils.dj import may_be_json
from asv_files.dj.models import *
from asv_files.dj.settings import settings as AFS
#---------------------------------------------------------------
#---------------------------------------------------------------
class AsvFileForm(forms.ModelForm):
    class Meta:
        widgets = {
             'title': forms.TextInput(attrs={'style':'width:200px;',}),
        }
class AsvFileInline(generic.GenericStackedInline):
    model = AsvFile
    form  = AsvFileForm
    #template = 'asv_files__admin__stacked.html'
    extra=0
#---------------------------------------------------------------
#---------------------------------------------------------------
class AsvFileAdmin(admin.ModelAdmin):
    pass
admin.site.register(AsvFile, AsvFileAdmin)
#---------------------------------------------------------------
#---------------------------------------------------------------
class UploaderTmpFileInline(admin.StackedInline):
    model=UploaderTmpFile
    #template = 'asv_files__admin__stacked.html'
    extra=0
class UploaderSessAdmin(admin.ModelAdmin):
    inlines=(UploaderTmpFileInline,)
admin.site.register(UploaderSess, UploaderSessAdmin)
#---------------------------------------------------------------
#---------------------------------------------------------------
@login_required
@may_be_json
def adminRPC_filesort(request, *args, **kwargs):
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
            except Exception as e:
                Mod = False
        if Mod and OrderId:
            Order = []
            id2id = re.compile(r'file_(\d+)')
            for i in OrderId:
                ok = id2id.match(i)
                if ok:
                    Order.append(Str2Int(ok.group(1)))
            Files = Mod.objects.filter(id__in=Order)
            Files[0].change_position_order(Order)
            Result['status'] = 'OK'
        else:
            Result['status'] = 'ERR'
            #del Result['csrfmiddlewaretoken']
    else:
        Result['status'] = 'ERR'
        #---------------
    return Result
#---------------------------------------------------------------
#---------------------------------------------------------------
