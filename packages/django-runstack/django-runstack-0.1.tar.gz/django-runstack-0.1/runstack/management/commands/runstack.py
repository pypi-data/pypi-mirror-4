import re
import threading
from optparse import make_option
from django.conf import settings
from django.utils import autoreload
from django.core import management
from django.core.management.base import BaseCommand


class ThreadRunner(threading.Thread):

    def __init__(self, cmd_name, *args, **kwargs):
        threading.Thread.__init__(self, name=cmd_name)
        self.cmd_name = cmd_name
        self.args = args
        self.kwargs = kwargs

    def run(self):
        management.call_command(self.cmd_name, *self.args, **self.kwargs)


class Command(BaseCommand):
    help = 'Run the fully configured dev stack.'

    def handle(self, *args, **options):
        def inner_run():
            threads = []
            threads.append(ThreadRunner('runserver'))
            threads.append(ThreadRunner('runsmtpd'))

            for thread in threads:
                thread.setDaemon(1)
                thread.start()

        autoreload.main(inner_run)
