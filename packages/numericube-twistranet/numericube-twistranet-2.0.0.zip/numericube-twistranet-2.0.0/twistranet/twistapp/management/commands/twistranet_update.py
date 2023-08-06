"""
Perform database repairings.
Handy for bootstraping the application!
"""
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

class Command(BaseCommand):
    args = ''
    help = 'Update your TwistraNet installation. Use this to load theme in your project.'

    def handle(self, *args, **options):
        call_command('syncdb', interactive=False)
        from twistranet.core import install
        install.install_theme()
