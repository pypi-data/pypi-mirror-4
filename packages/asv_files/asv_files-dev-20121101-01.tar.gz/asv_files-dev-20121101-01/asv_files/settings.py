# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from asv_media.settings import settings as AMS
import os

ASV_FILES__DEBUG = False
ASV_FILES__KB = 1024
ASV_FILES__MB = ASV_FILES__KB * ASV_FILES__KB

ASV_FILES__UUID_LENGTH = 36
ASV_FILES__DELTA = 10

ASV_FILES__MEDIA_PATH = 'asv_files' # relative path in FileStorage
ASV_FILES__STORE_PATH = '{0}/files'.format(ASV_FILES__MEDIA_PATH.rstrip(os.sep))
ASV_FILES__TMP_STORE_PATH = '{0}/tmp'.format(ASV_FILES__MEDIA_PATH.rstrip(os.sep))
ASV_FILES__FILE_STORAGE = None
ASV_FILES__TMP_FILE_STORAGE = None

ASV_FILES__UPLOADER__RUNTIMES = 'html5,flash,silverlight,html4'
ASV_FILES__UPLOADER__CHUNK_SIZE = None #'64kb'
ASV_FILES__UPLOADER__MAX_FILE_SIZE = '1G'
ASV_FILES__UPLOADER__IMG_RESIZE = None
ASV_FILES__UPLOADER__FILE_FILTERS = [
        {'title' : 'Image files', 'extensions' : 'jpg,gif,png'},
        {'title' : 'Zip files',   'extensions' : 'zip',}
]
#ASV_FILES__UPLOADER__IMG_RESIZE = {
#    'width' : 320,
#    'height' : 240,
#    'quality' : 90,
#}
ASV_FILES__UPLOADER__PROTECT_FILES_ON_SUBMIT = True
ASV_FILES__UPLOADER__CTFILES_FIELD_WIDGET_TEMPLATE = 'asv_files/ctfiles_field_formwidget.html'
ASV_FILES__UPLOADER__MEDIA = {
    'css': {
    },
    'js': (
        '{0}'.format(AMS.ASV_MEDIA__JQUERY_JSON_LOCATION),
        '{0}/plupload.full.js'.format(AMS.ASV_MEDIA__PLUPLOAD_ROOT),
        '{0}/asv_files/js/ctfiles_formfield_widget.js'.format(AMS.ASV_MEDIA__STATIC_ROOT),
    )
}
#---------------------------------------------------------------
ASV_FILES__UPLOADER__MESSAGES = {
    'YES': 'Да',
    'NO': 'Нет',
    'OK': 'OK',
    'ERROR': 'ERROR',
    'HTTP_ERROR': 'HTTP-ERROR',
    'FILE_SIZE_ERROR': 'Файл слишком велик',        # NEED!!!!!
    'UPLOAD_FILES': '[Загрузить файлы на сервер]',
    'ADD_FILES': '[Select files]',
    'ALREADY': 'уже',
    'LOADED':  'загружен',
}
