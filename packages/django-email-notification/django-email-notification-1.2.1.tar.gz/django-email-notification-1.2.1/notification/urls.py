# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('notification.views',

    url(r'^register/$', 'register', name='register_notification'),
    url(r'^unregister/(?P<md5>[\d\w]+)/$', 'unregister', name='unregister_notification'),

    url(r'^list/$', 'notification_list', name='notification_list'),
    url(r'^$', 'edit_notification', name='create_notification'),
    url(r'^(?P<notification_id>[\d\w]+)/$', 'edit_notification', name='edit_notification'),

    url(r'^view/(?P<md5>[\d\w]+)/$', 'view_notification', name='view_notification'),

    url(r'^track/(?P<notification_md5>[\d\w]+)/(?P<item_pk>[\d\w]+)/(?P<recipient_md5>[\d\w]+)/$', 'track_link', name='track_link')
)
