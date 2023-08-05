__author__ = 'cternus'
from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
    url(r'^generate/$', 'gametex_print.views.gametex', name='gametex'),
    )
