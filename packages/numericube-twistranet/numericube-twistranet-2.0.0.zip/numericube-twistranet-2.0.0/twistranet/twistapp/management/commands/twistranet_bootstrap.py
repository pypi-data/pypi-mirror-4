"""
Perform database repairings.
Handy for bootstraping the application!
"""
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

class Command(BaseCommand):
    args = ''
    help = 'Bootstrap your TwistraNet installation. Use this to load initial data and start playing with TN.'

    def handle(self, *args, **options):
        call_command('syncdb', interactive=False)
        from twistranet.core import bootstrap
        bootstrap.bootstrap()
