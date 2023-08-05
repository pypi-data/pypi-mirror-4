# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from rblog.feeds import AllFeed, TagFeed
from rblog.views import BlogIndexView, PostDetailView, PostsWithTag, PostsByDate, AJAXPostsYear


urlpatterns = patterns('',
    url(r'^$',                                     BlogIndexView.as_view(), {}, 'app_blog-index'),
    url(r'^page/(?P<page>\d+)/$',                  BlogIndexView.as_view(), {}, 'app_blog-index-page'),
    url(r'^(?P<slug>[-\w]+)\.html$',               PostDetailView.as_view(), {}, 'app_blog-post-detail'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$',    PostsByDate.as_view(), {}, 'app_blog-archive'),
    url(r'^tag-(?P<tag>[-_A-Za-z0-9]+)/$',         PostsWithTag.as_view(), {}, 'app_blog-with_tag'),
    url(r'^tag-(?P<tag>[-_A-Za-z0-9]+)/page/(?P<page>\d+)/$',         PostsWithTag.as_view(), {}, 'app_blog-with_tag_page'),
    url(r'^tag-(?P<tag>[-_A-Za-z0-9]+)/feed/$',    TagFeed(), {}, 'app_blog-tagfeed'),
    url(r'^tag-(?P<tag>[-_A-Za-z0-9]+)/feed.rss$', TagFeed(), {}, 'app_blog-tagfeed2'),
    url(r'^feed/$',                                AllFeed(), {}, 'app_blog-feed'),
    url(r'^feed.rss$',                             AllFeed(), {}, 'app_blog-feed2'),
    url(r'^ajax/posts/$',                     AJAXPostsYear.as_view(), {}, 'app_blog-ajaxpostsyear'),
)


