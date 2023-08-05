# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.forms import CharField, Textarea
from django.utils import simplejson as json
from django.forms.util import *
from asv_files.dj.settings import settings as AFS
from asv_files.dj.models import *
#---------------------------------------------------------------
#---------------------------------------------------------------
class CTfilesFieldFormWidget(Textarea):
    def __init__(self, attrs=None):
        default_attrs = {
            #'rel': 'AsvTextarea',
            'class': 'asv_files_cfg',
        }
        if attrs:
            default_attrs.update(attrs)
        super(CTfilesFieldFormWidget, self).__init__(default_attrs)

    def render(self, name, value, attrs=None):
        if value is None: value = ''
        return render_to_string(AFS.ASV_FILES__UPLOADER__CTFILES_FIELD_WIDGET_TEMPLATE, {
            'final_attrs': mark_safe(flatatt(self.build_attrs(attrs, name=name))),
               'ta_value': conditional_escape(force_unicode(value)),
                'cfg_url': reverse('asv_files:formfield_config'),
                     'sr': settings.STATIC_URL.rstrip('/'),
        })
    class Media:
        css = AFS.ASV_FILES__UPLOADER__MEDIA['css']
        js = AFS.ASV_FILES__UPLOADER__MEDIA['js']
#---------------------------------------------------------------
#---------------------------------------------------------------
class CTfilesFormField(CharField):
    widget = CTfilesFieldFormWidget
    def __init__(self, *args, **kwargs):
        super(CTfilesFormField, self).__init__(*args, **kwargs)
        if not self.initial:
            self.initial = {}
        #self.initial = json.dumps(self.initial)
        try:
            self.initial = json.dumps(self.initial)
        except (ValueError, TypeError):
            self.initial = ''
    def to_python(self, value):
        data = {}
        if value:
            try:
                data = json.loads(value)
            except (ValueError, TypeError) as e:
                return None
        if not data:
            return None
        ffid = data.get('FORMFIELD_ID')
        if not ffid:
            if AFS.ASV_FILES__DEBUG:
                logger.error('asv_files::Uploader No FIELD-ID in the POST data.')
            return None
        try:
            UplSess = UploaderSess.objects.get(uuid=ffid)
        except Exception as e:
            if AFS.ASV_FILES__DEBUG:
                logger.error('asv_files::Uploader Session with name {0} not found.\n{1}'.format(ffid,e))
            return None
        return UplSess
#---------------------------------------------------------------
#---------------------------------------------------------------
#class CTfilesModelField(models.TextField):
#    def __init__(self, *args, **kwargs):
#        self.model = kwargs.pop('model',None)
#        super(CTfilesModelField, self).__init__(*args, **kwargs)
#    def formfield(self, **kwargs):
#        defaults = {
#                'widget': CTfilesFieldFormWidget, # forms.Textarea,
#            'form_class': CTfilesFieldFormField,  # forms.TimeField
#        }
#        defaults.update(kwargs)
#        #print(defaults)
#        rv = super(CTfilesModelField, self).formfield(**defaults)
#        rv.widget = CTfilesFieldFormWidget()
#        #e = open('/tmp/qq', 'wb')
#        #pickle.dump(rv,e)
#        #e.close()
#        return rv
#    #def to_python(self, value):
#    #    rv = super(AsvTxtField, self).to_python(value)
#    #    rv = creole2html(rv)
#    #    return rv
##add_introspection_rules([], ['asv_txt\.fields\.AsvTxtField$'])
#---------------------------------------------------------------
#---------------------------------------------------------------
