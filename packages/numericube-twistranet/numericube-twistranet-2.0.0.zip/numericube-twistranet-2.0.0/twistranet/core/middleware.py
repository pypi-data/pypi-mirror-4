"""
Middlewares for twistranet
"""
from django.conf import settings
from django.core import signals
from django.core.urlresolvers import get_script_prefix
from twistranet.twistapp.lib.log import *

def set_runtime_paths(sender,**kwds):
    """Dynamically adjust path settings based on runtime configuration.

    This function adjusts various path-related settings based on runtime
    location info obtained from the get_script_prefix() function.
    It also adds settings.BASE_URL to record the root of the Django server,
    and settings.BASE_DOMAIN to record the root of your domain.
    """
    # We only want to run this once; the signal is just for bootstrapping
    signals.request_started.disconnect(set_runtime_paths)
    base_url = get_script_prefix()
    while base_url.endswith("/"):
        base_url = base_url[:-1]
    settings.BASE_URL = base_url
    url_settings = settings.BASE_URL_DEPDENDANT
    if not base_url:
        base_url = '/'  # Empty means root
    
    for setting in url_settings:
        oldval = getattr(settings,setting)
        if "://" not in oldval and not oldval.startswith(base_url):
            if not oldval.startswith("/"):
                oldval = "/" + oldval
            setattr(settings, setting, settings.BASE_URL + oldval)
            
    # Special treatment for tinymce which doesn't use regular django settings mechanism
    import tinymce.settings
    oldval = tinymce.settings.JS_URL
    if "://" not in oldval and not oldval.startswith(base_url):
        if not oldval.startswith("/"):
            oldval = "/" + oldval
        tinymce.settings.JS_URL = settings.BASE_URL + oldval

class RuntimePathsMiddleware:
    """Middleware to re-configure paths at runtime.

    This middleware class doesn't do any request processing.  Its only
    function is to connect the set_runtime_paths function to Django's
    request_started signal.  We use a middleware class to be sure that it's
    loaded before any requests are processed, but need to trigger on a signal
    because middleware is loaded before the script prefix is set.
    """
    def __init__(self):
        signals.request_started.connect(set_runtime_paths)



