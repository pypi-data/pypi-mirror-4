# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings as DJS
from asv_files import settings as DEF

class Settings(object):
    def __init__(self):
        for setting in dir(DEF):
            if setting == setting.upper():
                setattr(self, setting, getattr(DEF, setting))
        DJS_d = dir(DJS)
        for setting in dir(self):
            if setting == setting.upper():
                s = None
                try:
                    DJS_d.index(setting)
                    s = getattr(DJS, setting)
                except ValueError:
                    pass
                if s:
                    setattr(self, setting, s)
        self.SETTINGS_MODULE = DEF
        self.ASV_FILES__FILE_STORAGE = self.ASV_FILES__FILE_STORAGE or DJS.DEFAULT_FILE_STORAGE
        self.ASV_FILES__TMP_FILE_STORAGE = self.ASV_FILES__TMP_FILE_STORAGE or DJS.DEFAULT_FILE_STORAGE
    #
settings = Settings()


