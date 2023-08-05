# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

urlpatterns = patterns('fakeimg.views',
    url(r'^(?P<width>\d+)/$', 'placeholder', name='fakeimg_placeholder'),
    url(r'^(?P<width>\d+)/(?P<bgd>([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3}))/$',
        'placeholder', name='fakeimg_placeholder'),
    url(r'^(?P<width>\d+)/(?P<bgd>[A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})/(?P<fgd>[A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})/$',
        'placeholder', name='fakeimg_placeholder'),
    url(r'^(?P<width>\d+)x(?P<height>\d+)/$', 'placeholder', name='fakeimg_placeholder'),
    url(r'^(?P<width>\d+)x(?P<height>\d+)/(?P<bgd>([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3}))/$',
        'placeholder', name='fakeimg_placeholder'),
    url(r'^(?P<width>\d+)x(?P<height>\d+)/(?P<bgd>[A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})/(?P<fgd>[A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})/$',
        'placeholder', name='fakeimg_placeholder'),
)

