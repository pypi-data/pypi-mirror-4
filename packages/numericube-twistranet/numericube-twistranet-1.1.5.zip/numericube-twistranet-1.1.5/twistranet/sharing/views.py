"""
Tags-specific views, including JSON stuff.
"""
import urllib
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import RequestContext, loader
from django.shortcuts import *
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.conf import settings
from django.core.paginator import Paginator, InvalidPage
from django.db.models import Q

try:
    # python 2.6
    import json
except:
    # python 2.4 with simplejson
    import simplejson as json

from twistranet.twistapp.models import Content, Account
from twistranet.twistapp.forms import form_registry
from twistranet.twistapp.lib.log import *
from twistranet.core.views import *



class LikeToggleView(BaseObjectActionView):
    """
    Like / Unlike switcher
    return html ajax response.
    """
    model_lookup = Content
    name = "like_toggle_by_id"
    template = "sharing/summary.part.html"


    def prepare_view(self, *args, **kw):
        """
        """
        super(LikeToggleView, self).prepare_view(*args, **kw)
        likes = self.content.likes()
        n_likes = likes['n_likes']
        if not likes['i_like']:
            self.content.like()
        else:
            self.content.unlike()

    def render_view(self,):
        t = get_template(self.template)
        params = {'content': self.content}
        c = RequestContext(self.request, params)
        return HttpResponse(t.render(c))

