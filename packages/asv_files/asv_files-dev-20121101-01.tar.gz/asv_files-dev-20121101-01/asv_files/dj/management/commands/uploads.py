# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError
from asv_files.dj.settings import settings as AFS
from asv_files.dj.models import UploaderSess
from optparse import make_option
from django.utils import timezone


#---------------------------------------------------------------
#---------------------------------------------------------------
class Command(BaseCommand):
    args = '<sess_ID or filename>'
    help = 'Managament for upload files and sessions'
    requires_model_validation = True
    output_transaction = True

    QS = UploaderSess.objects

    option_list = BaseCommand.option_list + (
        make_option('--sessions',
            action='store_true',
            dest='sessions',
            default=False,
            help='list unclosed upload sessions and it\'s files, if exist'),
        make_option('--realname',
            action='store_true',
            dest='realname',
            default=False,
            help='display real (user\'s) file name near file name'),
        make_option('--no-files', '--nofiles',
            action='store_true',
            dest='no-files',
            default=False,
            help='do not display information about files'),
        make_option('--older',
            action='store',
            type='float',
            dest='older',
            default=0,
            metavar='XX',
            help='use only sessions older than XX hours'),
        make_option('--only-uuids', '--onlyuuids',
            action='store_true',
            dest='only-uuids',
            default=False,
            help='show only session\'s UUIDs'),
#        make_option('--lost-files',
#            action='store_true',
#            dest='lost-files',
#            default=False,
#            help='list files in storage without session'),
        make_option('--remove',
            action='store_true',
            dest='remove',
            default=False,
            help='remove upload session and her files'),
    )

    def get_td(self, hours):
        m = int(hours * 60)
        return timezone.now() - timezone.timedelta(minutes=m)
    def get_filesize(self, f):
        fsize = f.get_filesize()
        if fsize and fsize > 0:
            fsize = '{0:>18.0f} Kb'.format(fsize / AFS.ASV_FILES__KB)
        else:
            fsize = '{0:>21}'.format('not-found')
        return fsize


    def do_sessions(self, *args, **options):
        qs = self.QS
        if not options['no-files']:
            qs = qs.select_related(depth=1)
        if options['older'] and options['older'] > 0:
            SS = qs.filter(de__lt=self.get_td(options['older']))
        else:
            SS = qs.all()
        for s in SS.order_by('de'):
            if options['only-uuids']:
                self.stdout.write('{0} '.format(s.uuid))
            else:
                self.stdout.write('{0}\n'.format(s))
                if not options['no-files']:
                    for f in s.files.all():
                        fsize = self.get_filesize(f)
                        rn = '"{0}"'.format(f.get_realname()) if options['realname'] else ''
                        self.stdout.write('{size:>18}  {file}  {realname}\n'.format(
                            file = f,
                            size = fsize,
                            realname = rn,
                        ))
        self.stdout.write('\n')

    def do_remove(self, *args, **options):
        if len(args) < 1:
            raise CommandError('No session ID given!')
        for s in self.QS.filter(uuid__in=args):
            s.delete()

    def do_lost_files(self, *args, **options):
        pass

    def handle(self, *args, **options):
        #if settings.DEBUG:
        #    for i in args:
        #        self.stdout.write('args: {0}\n'.format(i))
        #    for i in options:
        #        self.stdout.write('opt: {0}={1}\n'.format(i, options[i]))
        #    self.stdout.write('---\n')
        if options['sessions']:
            self.do_sessions(*args, **options)
#        elif options['lost-files']:
#            self.do_lost_files(*args, **options)
        elif options['remove']:
            self.do_remove(*args, **options)
#-------------------------------------------------------------------
#-------------------------------------------------------------------
