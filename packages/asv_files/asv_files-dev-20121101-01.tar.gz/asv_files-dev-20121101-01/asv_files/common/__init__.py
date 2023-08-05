# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from asv_files import settings
import uuid as x_uuid

__description__ = '''
Batteries for multiupload files in forms (custom formfield).
Ajax multi-upload FormField
'''

class uuid(unicode):
    '''
    generate uuid for all functions in this library.
    '''
    def __new__(cls, x=''):
        val=unicode(x_uuid.uuid4())[:settings.ASV_FILES__UUID_LENGTH]
        return unicode.__new__(cls, val)
