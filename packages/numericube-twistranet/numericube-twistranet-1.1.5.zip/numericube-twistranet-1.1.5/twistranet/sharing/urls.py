from django.conf.urls.defaults import *
from twistranet.core.views import AsView
from views import *


urlpatterns = patterns('sharing',
    url(r'^like_toggle_by_id/(\d+)$', AsView(LikeToggleView, lookup = 'id'), name=LikeToggleView.name),
    url(r'^like_toggle_by_slug/(\d+)$', AsView(LikeToggleView, lookup = 'slug'), name=LikeToggleView.name),
)
