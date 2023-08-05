try:
    from django.conf.urls import patterns, include, url
except ImportError:
    from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^complete/$', 'cccontact.views.complete', name='complete'),
    url(r'^$', 'cccontact.views.contact', name='contact')
)
