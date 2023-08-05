# -*- coding:utf-8 -*-

from django.conf.urls import patterns

urlpatterns = patterns('forum.views',
    (r'^$',
        'index_view', {}, 'index'),

    # your own profile
    (r'^profile/$',
        'profile_view', {}, 'profile'),

    # edit your own profile
    (r'^profile/edit/$',
        'edit_profile_view', {}, 'edit_profile'),

    # someone's profile
    (r'^profile/(?P<nickname>[\w\-\+\.@]+)/$',
        'public_profile_view', {}, 'profile'),

    # send someone a message
    (r'^profile/(?P<nickname>[\w\-\+\.@]+)/send_message/$',
        'send_message_view', {}, 'send_message'),

    # see your own messages
    (r'^messages/$',
        'messages_view', {}, 'messages'),

    # read your own message
    (r'^messages/(?P<pk_message>\d+)/$',
        'messages_view', {}, 'messages'),

    # see forum under this category
    (r'^category/(?P<pk_category>[\w\-\+\.@]+)/$',
        'category_view', {}, 'category'),
#
    # see forum
    (r'^(?P<pk_forum>\d+)/$',
        'forum_view', {}, 'expose'),

    # post a new thread
    (r'^(?P<pk_forum>\d+)/threads/new/$',
        'new_thread_view', {}, 'new_thread'),

    # read a thread
    (r'^(?P<pk_forum>\d+)/threads/(?P<pk_thread>\d+)/$',
        'thread_view', {}, 'thread'),
#
#    # edit a thread
#    (r'^(?P<pk_forum>\d+)/threads/(?P<pk_thread>\d+)/edit/$',
#        'edit_thread_view', {}, 'edit_thread'),

    # reply to a thread
    (r'^(?P<pk_forum>\d+)/threads/(?P<pk_thread>\d+)/reply/$',
        'reply_view', {}, 'reply'),

#    # rate a thread
#    (r'^(?P<pk_forum>\d+)/threads/(?P<pk_thread>\d+)/reply/(?P<pk_reply>\d+)/rate/$',
#        'rate_reply_view', {}, 'rate'),
)
