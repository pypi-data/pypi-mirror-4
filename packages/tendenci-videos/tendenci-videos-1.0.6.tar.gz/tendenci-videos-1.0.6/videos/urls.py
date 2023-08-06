from django.conf.urls.defaults import *
from videos.feeds import LatestEntriesFeed
from tendenci.core.site_settings.utils import get_setting

urlpath = get_setting('module', 'videos', 'url')
if not urlpath:
    urlpath = "videos"

urlpatterns = patterns('videos.views',
    url(r'^%s/$' % urlpath, 'search', name="video"),
    url(r'^%s/category/([^/]+)/$'  % urlpath, 'index', name="video.category"),
    url(r'^%s/search/$' % urlpath, 'search', name="video.search"),
    url(r'^%s/feed/$' % urlpath, LatestEntriesFeed(), name='video.feed'),
    url(r'^%s/([^/]+)/$' % urlpath, 'detail', name="video.details"),
)