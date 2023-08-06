''' Adapted from django-mailpers (https://github.com/bluszcz/django-mailpers)
'''
import sys
import asyncore
from smtpd import DebuggingServer
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


EMAIL_HOST = getattr(settings, 'EMAIL_HOST', '127.0.0.1')
EMAIL_PORT = getattr(settings, 'EMAIL_PORT', '1025')


class Command(BaseCommand):
    help = 'Starts SMTP development server (using variables from the settings)'

    def handle(self, *args, **kargs):
        if EMAIL_HOST not in ['localhost', '127.0.0.1']:
            sys.stdout.write('EMAIL_HOST {host} doesn\'t look like '
                             'local one'.format(host=EMAIL_HOST))
            sys.stdout.flush()
        DebuggingServer((EMAIL_HOST, EMAIL_PORT), ('localhost', 25))
        sys.stdout.write(
            'Started development SMTP server {host}:{port}, '
            'hit Ctrl-C to stop\n'.format(host=EMAIL_HOST, port=EMAIL_PORT)
        )
        sys.stdout.flush()
        asyncore.loop()
