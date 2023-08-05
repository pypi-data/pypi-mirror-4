# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.utils.encoding import smart_unicode
from django.views.generic.base import View
from django.utils.decorators import method_decorator
from django.http import   HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from asv_files.dj.settings import settings as AFS
from asv_media.settings import settings as AMS
from asv_utils.dj import may_be_json
from asv_files.dj.models import UploaderSess
from asv_utils.common import CleanFileName
import logging
logger = logging.getLogger('asv_files')

#----------------------------------------------------------------
Forbidden = HttpResponseForbidden('<h1>Forbiden!!!</h1>')
#----------------------------------------------------------------
#----------------------------------------------------------------
class FormFieldConfig(View):
    _DEBUG = AFS.ASV_FILES__DEBUG
    _logger = logger
    _UploaderSess = None
    _FormfieldID = None
    _cfg_file_filters = AFS.ASV_FILES__UPLOADER__FILE_FILTERS
    _cfg_messages = AFS.ASV_FILES__UPLOADER__MESSAGES

    def _get_base_config_url(self):
        return reverse('asv_files:formfield_config').rstrip('/')
    def _get_file_upload_url(self):
        return reverse('asv_files:formfield_file_upload', args=[self._FormfieldID,])
    def _get_file_filters(self):
        return self._cfg_file_filters
    def _get_messages(self):
        return self._cfg_messages
    def _get_file_list(self):
        if self._UploaderSess:
            rv =  [
                {
                    'name': f.get_realname(),
                      'id': f.get_fileid(),
                    'size': f.get_filesize(),
                } for f in self._UploaderSess.get_files()
            ]
        else:
            rv = ()
        return rv
    def _get_plupload_cfg(self):
        rv = {
            'runtimes' : AFS.ASV_FILES__UPLOADER__RUNTIMES,
            'container': 'cnt-{0}'.format(self._FormfieldID),
            'file_list': 'fl-{0}'.format(self._FormfieldID),
            'browse_button' : 'add-{0}'.format(self._FormfieldID),
            'start_uploads_button': 'upl-{0}'.format(self._FormfieldID),
            'unique_names' : True,
            'url' : self._get_file_upload_url(),
            'flash_swf_url' : '{0}/plupload.flash.swf'.format(AMS.ASV_MEDIA__PLUPLOAD_ROOT),
            'silverlight_xap_url' : '{0}/plupload.silverlight.xap'.format(AMS.ASV_MEDIA__PLUPLOAD_ROOT),
            'filters' : self._get_file_filters(),
        }
        if AFS.ASV_FILES__UPLOADER__CHUNK_SIZE:
            rv['chunk_size'] = AFS.ASV_FILES__UPLOADER__CHUNK_SIZE
        if AFS.ASV_FILES__UPLOADER__IMG_RESIZE:
            rv['resize'] = AFS.ASV_FILES__UPLOADER__IMG_RESIZE
        if AFS.ASV_FILES__UPLOADER__MAX_FILE_SIZE:
            rv['max_file_size'] = AFS.ASV_FILES__UPLOADER__MAX_FILE_SIZE
        return rv

    @method_decorator(may_be_json)
    def post(self, request, FID=None, **kwargs):
        if not request.is_ajax() and not self._DEBUG:
            if self._DEBUG:
                self._logger.info('ASV_FILES::Uploader-config::403-non-AJAX request.')
            return Forbidden
        if FID:
            FID = FID.strip('/')
            self._FormfieldID = FID
            self._UploaderSess = UploaderSess.check_req_uuid(request, FID)
            if not self._UploaderSess:
                if self._DEBUG:
                    self._logger.info('ASV_FILES::Uploader-config::403-session not found in DB.')
                return Forbidden
        else:
            self._FormfieldID = UploaderSess.create(request).uuid
        return {
            'FORMFIELD_ID': self._FormfieldID,
            'URL_CONFIG': '{0}/{1}/'.format(self._get_base_config_url(), self._FormfieldID),
            'FILES': self._get_file_list(),
            'PLUPLOAD_CFG': self._get_plupload_cfg(),
            'PROTECT_FILES_ON_SUBMIT': AFS.ASV_FILES__UPLOADER__PROTECT_FILES_ON_SUBMIT,
            'MESSAGES': self._get_messages(),
        }
#----------------------------------------------------------------
#----------------------------------------------------------------
class FileUpload(View):
    _DEBUG = AFS.ASV_FILES__DEBUG
    _logger = logger
    def _cleanFileName(self, name):
        return CleanFileName(name)
    def _get_file_path_in_storage(self):
        return AFS.ASV_FILES__TMP_STORE_PATH.rstrip('/')
    def _get_dst_file_path(self, name):
        return '{dir}/{fname}'.format(
            fname=self._cleanFileName(name),
            dir=self._get_file_path_in_storage(),
        )

    @method_decorator(may_be_json)
    def post(self, request, FID=None, **kwargs):
        FID = FID.strip('/')
        if not FID and not settings.DEBUG:
            if self._DEBUG:
                self._logger.info('ASV_FILES::Uploader::403-no_FID')
            return Forbidden
        UplSession = UploaderSess.check_uuid(FID)
        if not UplSession:
            if self._DEBUG:
                self._logger.info('ASV_FILES::Uploader::403-session not found in DB.')
            return Forbidden
        # session valid, saving and attach files
        file_id = request.POST.get('name')
        if file_id:
            file_id = file_id.split('.')[0]
        postF = request.FILES.get('file')
        if not postF:
            return Forbidden
        UplFileRecord = UplSession.files.create()
        FS = UplFileRecord.get_filestorage()
        dstF = FS.save(self._get_dst_file_path(postF.name), postF)
        UplFileRecord.file = dstF
        UplFileRecord.file_id = file_id
        UplFileRecord.realname = smart_unicode(postF.name)
        UplFileRecord.save()
        if self._DEBUG:
            logger.info('asv_files::file {f} saved.'.format(f=dstF))
        rv = {
            'FID': FID,             # form ID
            'FILE_ID': file_id,     # file ID
        }
        return rv
    # disable CSRF protection
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(FileUpload, self).dispatch(*args, **kwargs)
#----------------------------------------------------------------
#----------------------------------------------------------------
