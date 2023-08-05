from django.conf.urls.defaults import patterns, include, url
from hadrian.contrib.forum.views import *


urlpatterns = patterns('',

    url(r'^$', home, name="home"),
    url(r'^new_topic/(?P<forum_slug>[-\w]+)/$', new_topic, name="new_topic"),
    url(r'^(?P<forum_slug>[-\w]+)/$', forum, name="forum"),
    url(r'^(?P<forum_slug>[-\w]+)/(?P<topic_slug>[-\w]+)/$', topic, name="topic"),
    
)
