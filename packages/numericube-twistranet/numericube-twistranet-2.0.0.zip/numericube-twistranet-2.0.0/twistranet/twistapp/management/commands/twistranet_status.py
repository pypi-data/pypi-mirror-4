"""
Report status over this TN instance, as a table.
"""
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Max
from django.conf import settings
import os

class Command(BaseCommand):
    args = ''
    help = 'Bootstrap your TwistraNet installation. Use this to load initial data and start playing with TN.'

    def handle(self, *args, **options):
        """
        Perform stats
        """
        from twistranet.twistapp import UserAccount, Content, SystemAccount
        from django.contrib.auth.models import User
        __account__ = SystemAccount.get()
        here = os.path.split(settings.HERE)[1]
        stat_dict = {
            "here":             here,
            "n_users":          UserAccount.objects.count(),
            "n_contents":       Content.objects.count(),
            "last_login":       User.objects.aggregate(Max("last_login"))['last_login__max'].strftime("%Y-%m-%d"),
        }
        print "%(here)32s | %(n_users)4d Users | %(n_contents)5d Contents | %(last_login)s" % stat_dict
        
