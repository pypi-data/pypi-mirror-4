# -*- coding: utf-8 -*-

try:
    from django.conf.urls.defaults import patterns, url
except ImportError:  # Django 1.5
    from django.conf.urls import patterns, url


urlpatterns = patterns('inplaceeditform.views',
    url(r'^save/$', 'save_ajax', name='inplace_save'),
    url(r'^get_field/$', 'get_field', name='inplace_get_field')
)
