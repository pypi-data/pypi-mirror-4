from django.conf.urls.defaults import *

from csnews.feeds import LatestNews, LatestComments
#feed_dict = {'rss': LatestNews}

urlpatterns = patterns('',
    (r'^$','csnews.views.index'),
    (r'^feed/$', LatestNews()),
    (r'^comment-feed/$', LatestComments()),
    (r'^hemeroteka/', 'csnews.views.hemeroteka'),            
    (r'^(?P<article_slug>[\-\d\w]+)/$','csnews.views.article_index'),
)

