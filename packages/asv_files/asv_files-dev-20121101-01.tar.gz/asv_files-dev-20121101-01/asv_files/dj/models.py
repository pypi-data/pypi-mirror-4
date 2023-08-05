# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.files.storage import get_storage_class
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.utils.decorators import classonlymethod
from django.utils.encoding import smart_unicode
from django.utils.timezone import *

from asv_files.common import uuid
from asv_utils.common import CleanFileName #, Str2Int
from asv_files.dj.settings import settings as AFS
import os
import logging
logger = logging.getLogger('asv_files')
#from django.db.models.signals import *
#from django.core.exceptions import *
#from django.core.urlresolvers import reverse

#---------------------------------------------------------------
#---------------------------------------------------------------
asv_files__title_length = 128
class AsvFileBase(models.Model):
    FileStorePath = '{0}/asv_files'.format(AFS.ASV_FILES__STORE_PATH)
    def FileStoreName(instance, filename):
        '''
        returns a relative path to file, remove or deduplicate some character's
        '''
        return '{dir}/{fname}'.format(
            fname=CleanFileName(filename),
            dir=AFS.ASV_FILES__STORE_PATH.rstrip(os.sep)
        )
    #----------
    active = models.BooleanField(default=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object=generic.GenericForeignKey('content_type','object_id')
    prio   = models.PositiveIntegerField(default=65000, editable=False)
    #
    file    = models.FileField(max_length=65535, upload_to=FileStoreName, verbose_name='файл',
                storage=get_storage_class(AFS.ASV_FILES__FILE_STORAGE)())
    title   = models.CharField(max_length=asv_files__title_length, blank=True, verbose_name='описание')
    #mimetype= models.CharField(max_length=asv_files__title_length, blank=True, verbose_name='mime-type')
    #tags   = TaggableManager(blank=True)
    de     = models.DateTimeField(auto_now_add=True)
    lm     = models.DateTimeField(auto_now=True)
    #----------
    def change_position_order(self, ORD=[]):
        """
        Берем все файлы из данной модели, приаттаченые к одному и тому-же
        content_object, пытаемся упорядочить их в соответствии с порядком ID-ов
        из массива ORD.
        """
        if AFS.ASV_FILES__DEBUG:
            logger.info('ASV_FILES::change_position_order::begin')
        def recalc_files_prio(iis):
            delta = AFS.ASV_FILES__DELTA
            if delta < 10:
                delta = 10
            c = iis.count()
            if not (c > 0):
                return False
            a = 1
            for i in iis:
                t = a * delta
                if t != i.prio :
                    i.prio = t
                    i.save()
                a += 1
            return True

        CT = self.content_type
        OID= self.object_id
        Files = self.__class__.objects.filter(content_type=CT, object_id=OID)
        recalc_files_prio(Files)
        l = 0
        for i in ORD:
            if i == Files[l].id:
                l += 1
                continue
            # need change position
            try:
                cc = self.__class__.objects.get(id=i)
            except Exception as e:
                l += 1
                continue
            cc.prio = Files[l].prio - 1
            cc.save()
            Files = self.__class__.objects.filter(content_type=CT, object_id=OID)
            #
            l += 1
        recalc_files_prio(Files)
        if AFS.ASV_FILES__DEBUG:
            logger.info('ASV_FILES::change_position_order::end')
        return True
    def get_title(self, **kwargs):
        return  self.title or self.file.name
    def get_alt(self, *args, **kwargs):
        return self.get_title(args, **kwargs)
    def get_document(self):
        '''
        return object -- owner of this file
        '''
        return self.content_object
    def get_filepath(self):
        '''
        return path to file IN STORAGE
        '''
        return self.file.name
    def get_filename(self):
        '''
        return file (in storage) name without path
        '''
        return os.path.split(self.get_filepath())[1]
    def get_filestorage(self):
        return self.file.storage
    def delete(self, *args, **kwargs):
        '''
        remove file from storage
        remove file record from database
        '''
        fn = self.get_filepath()
        try:
            # update Djapian's index, if it is!
            self.__class__.indexer.delete(self)
        except Exception, e:
            if AFS.ASV_FILES__DEBUG:
                logger.info('asv_files::{0}::delete__update_djapian_index::{1}\n{2}'.format(
                    self.__class__.__name__,
                    e.__class__.__name__,
                    e
                ))
        try:
            self.file.delete(save=False)
            if AFS.ASV_FILES__DEBUG:
                logger.info('asv_files::{c}::delete::file {f} deleted.'.format(
                    c=self.__class__.__name__,
                    f=fn
                ))
        except Exception as e:
            if AFS.ASV_FILES__DEBUG:
                logger.error('asv_files::{0}::delete__remove_file::{1} {2}\n{3}'.format(
                    self.__class__.__name__,
                    fn,
                    e.__class__.__name__,
                    e
                ))
        super(AsvFileBase, self).delete(*args, **kwargs)

    def save(self, **kwargs):
        old = None
        try:
            old = self.__class__.objects.get(pk=self.pk)
        except Exception as e:
            pass
#            if AFS.ASV_FILES__DEBUG:
#                logger.info('asv_files::{0}::save__old_file_not_found::{1}\n{2}'.format(
#                    self.__class__.__name__,
#                    e.__class__.__name__,
#                    e
#                ))
        if old:
            oi = old.file
            ni = self.file
            if oi:
                if ((oi and ni) and (oi.path != ni.path)) or ((not ni) and oi):
                    fn = oi.file.name
                    try:
                        oi.delete(save=False)
                        if AFS.ASV_FILES__DEBUG:
                            logger.info('asv_files::{c}::save::old file {f} deleted.'.format(
                                c=self.__class__.__name__,
                                f=fn
                            ))
                    except Exception as e:
                        if AFS.ASV_FILES__DEBUG:
                            logger.error('asv_files::{c}::save__remove_old_file::{f}::{en}\n{et}'.format(
                                c = self.__class__.__name__,
                                f = fn,
                                en = e.__class__.__name__,
                                et = e
                            ))
        super(AsvFileBase, self).save(**kwargs)
        try:
            # update Djapian's index, if it is!
            self.__class__.indexer.update()
        except Exception as e:
            if AFS.ASV_FILES__DEBUG:
                logger.error('asv_files::{0}::save__update_djapian_index::{1}\n{2}'.format(
                    self.__class__.__name__,
                    e.__class__.__name__,
                    e
                ))
    def __unicode__(self):
        fid = self.id or '00'
        rv = '[{0}] {1}'.format(fid,self.get_title())
        return rv
    #
    class Meta:
        abstract = True
        ordering = ('content_type', 'prio', 'de')
        verbose_name='файл'
        verbose_name_plural='файлы'
#-------------------------------------------------------------------
#-------------------------------------------------------------------
class AsvFile(AsvFileBase):
    class Meta:
        ordering = ('content_type', 'prio', 'de')
        verbose_name='файл'
        verbose_name_plural='файлы'
#-------------------------------------------------------------------
#-------------------------------------------------------------------
class UploaderSess(models.Model):
    uuid   = models.CharField(max_length=AFS.ASV_FILES__UUID_LENGTH, unique=True)
    sess_key = models.CharField(max_length=40, db_index=True, null=True, blank=True)
    user   = models.ForeignKey(User, null=True, blank=True)
    de     = models.DateTimeField(auto_now_add=True)
    lm     = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ('user', 'sess_key', 'de')
        verbose_name='сессия мультиаплоада'
        verbose_name_plural='сессии мультиаплоада'
    def get_files(self):
        return self.files.all()
    def __unicode__(self):
        d = make_naive(self.de,get_current_timezone()).strftime('%Y-%m-%d %H:%M:%S')
        return smart_unicode('({date})  {uuid}'.format(uuid=self.uuid, date=d))
    @classonlymethod
    def create(cls, request):
        user = request.user if request.user.is_authenticated() else None
        sess_k = None if user else request.session.session_key
        rv = UploaderSess(uuid=uuid(), sess_key=sess_k, user=user)
        rv.save()
        return rv
    @classonlymethod
    def check_uuid(cls, uuid):
        try:
            rv = cls.objects.get(uuid=uuid)
        except cls.DoesNotExist:
            return False
        return rv
    @classonlymethod
    def check_req_uuid(cls, request, uuid):
        UpSession = cls.check_uuid(uuid)
        if not UpSession:
            return False
        user = request.user if request.user.is_authenticated() else None
        sess_key = request.session.session_key
        if user and not UpSession.user:
            return False
        elif user and UpSession.user != user:
            return False
        elif not user and UpSession.sess_key != sess_key:
            return False
        elif not user and not sess_key:
            return False
        UpSession.save()
        return UpSession
    def delete(self, *args, **kwargs):
        for i in self.get_files():
            try:
                i.delete()
            except Exception as e:
                if AFS.ASV_FILES__DEBUG:
                    logger.error('asv_files::{0}::delete::{1} non-fatal error.\n{2}'.format(
                        self.__class__.__name__,
                        e.__class__.__name__,
                        e
                    ))
        super(UploaderSess, self).delete(*args, **kwargs)
#-------------------------------------------------------------------
#-------------------------------------------------------------------
class UploaderTmpFile(models.Model):
    def FileStoreName(instance, filename):
        '''
        returns a relative path to file, remove or deduplicate some character's
        '''
        return '{dir}/{fname}'.format(
            fname=CleanFileName(filename),
            dir=AFS.ASV_FILES__TMP_STORE_PATH.rstrip(os.sep)
        )
    #----------
    usess   = models.ForeignKey('UploaderSess', related_name='files')
    file    = models.FileField(max_length=65535, upload_to=FileStoreName, verbose_name='файл', storage=get_storage_class(AFS.ASV_FILES__TMP_FILE_STORAGE)())
    file_id = models.CharField(max_length=AFS.ASV_FILES__UUID_LENGTH, verbose_name='ID файла', blank=True, default='')
    realname= models.CharField(max_length=65535, blank=True, default='')
    de      = models.DateTimeField(auto_now_add=True)
    lm      = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ('usess', 'de')
        verbose_name='временный файл мультиаплоада'
        verbose_name_plural='временные файлы мультиаплоада'
    def get_fileid(self):
        '''
        return file-ID generated on client side
        '''
        return self.file_id
    def get_filepath(self):
        '''
        return path to file IN STORAGE
        '''
        return self.file.name
    def get_filename(self):
        '''
        return file (in storage) name without path
        '''
        return os.path.split(self.get_filepath())[1]
    def get_filesize(self):
        try:
            rv = self.file.size
        except Exception as e:
            rv = -1
        return rv
    def get_realname(self):
        '''
        return real (on uploader side) file name
        '''
        return self.realname or self.get_filename()
    def get_filestorage(self):
        return self.file.storage
    def delete(self, *args, **kwargs):
        '''
        remove file from storage
        remove file record from database
        '''
        fn = self.get_filepath()
        try:
            self.file.delete(save=False)
            if AFS.ASV_FILES__DEBUG:
                logger.info('asv_files::{c}::delete::file {f} deleted.'.format(
                    c=self.__class__.__name__,
                    f=fn
                ))
        except Exception as e:
            if AFS.ASV_FILES__DEBUG:
                logger.error('asv_files::{0}::delete::{1}::{2}\n{3}'.format(
                    self.__class__.__name__,
                    fn,
                    e.__class__.__name__,
                    e
                ))
        super(UploaderTmpFile, self).delete(*args, **kwargs)
    def __unicode__(self):
        #return smart_unicode('{0}'.format(self.get_filename() or '<empty>'))
        return smart_unicode(self.get_filename() or '<empty>')
    def attach_to(self, obj, title='', realname=True, file_storage_cls=AsvFile):
        if AFS.ASV_FILES__DEBUG:
            logger.error('asv_files::{0}::attach_to::begin'.format(self.__class__.__name__))
        if realname:
            f_title = title or self.get_realname()
        else:
            f_title = title
        f_title = f_title[:asv_files__title_length]
        F = file_storage_cls(content_object=obj, title=f_title)
        dstFname = F.FileStoreName(self.get_filename())
        FS = F.get_filestorage()
        dstF = FS.save(dstFname,self.file)
        F.file = dstF
        F.save()
        if AFS.ASV_FILES__DEBUG:
            logger.error('asv_files::{0}::attach_to::end'.format(self.__class__.__name__))
        return True
#-------------------------------------------------------------------
#-------------------------------------------------------------------
