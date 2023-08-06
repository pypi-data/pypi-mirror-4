from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import redirect_to
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from views import *

urlpatterns = patterns(
    '',
    url(r'^$', nodes, name='nodes'),
    url(r'^config/$', config, name='config'),
    url(r'^-/edit/$', node_edit, name='node_edit'),
    url(r'^([^\/]+)/edit/$', node_edit, name='node_edit'),
    url(r'^([^\/]+)/$', node, name='node'),
    url(r'^([^\/]+)/actions/$', node_actions, name='node_actions'),
)
