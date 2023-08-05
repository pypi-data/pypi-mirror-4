from twistranet.compress import utils
import os
from django.conf import settings as django_settings
from django.utils.http import urlquote
from django.core.urlresolvers import reverse
from twistranet.twistapp.lib.log import *

def new_media_root(filename):
    """
    Return the full path to ``filename``. ``filename`` is a relative path name in TWISTRANET STATIC PATH
    """
    return os.path.join(django_settings.TWISTRANET_STATIC_PATH, filename)

def new_media_url(url):
    home_url = reverse("twistranet_home")
    return home_url + 'static/' + urlquote(url)

utils.old_media_root = utils.media_root
utils.media_root = new_media_root
utils.old_media_url = utils.media_url
utils.media_url = new_media_url
log.info("Hotfixed django.compress")