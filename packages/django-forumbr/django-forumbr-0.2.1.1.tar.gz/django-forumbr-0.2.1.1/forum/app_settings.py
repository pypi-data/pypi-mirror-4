# -*- coding:utf-8 -*-

from django.conf import settings

KB = 1024 # bytes
MB = 1024 * KB # kb
MIN = 60

MARKUP_FORCE_SAFE_HTML = getattr(settings, 'FORUM_MARKUP_FORCE_SAFE_HTML', True)
MARKUP = getattr(settings, 'FORUM_MARKUP', 'plain text') # plain text, bbcode, markdown, textile, restructuredtext, plain html

MAX_THREAD_IMAGE_SIZE = getattr(settings, 'FORUM_MAX_THREAD_IMAGE_SIZE', 120 * KB)
MAX_THREAD_ATTACH_SIZE = getattr(settings, 'FORUM_MAX_THREAD_ATTACH_SIZE', 2 * MB)
THREAD_ALLOW_IMAGE = getattr(settings, 'FORUM_THREAD_ALLOW_IMAGE', True)
THREAD_ALLOW_ATTACHMENT = getattr(settings, 'FORUM_THREAD_ALLOW_ATTACHMENT', True)

# em bytes
AVATAR_MAX_SIZE = getattr(settings, 'FORUM_AVATAR_MAX_SIZE', 40 * KB) # 40 kb

EDIT_REPLY = getattr(settings, 'FORUM_EDIT_REPLY', False)
EDIT_REPLY_TIME_LIMIT = getattr(settings, 'FORUM_EDIT_REPLY_TIME_LIMIT', 5 * MIN)
ALLOW_INLINE_REPLY = getattr(settings, 'FORUM_ALLOW_INLINE_REPLY', True)

# requires clamav and pyclamd
CHECK_ATTACH_FOR_VIRUS = getattr(settings, 'FORUM_CHECK_ATTACHMENT_FOR_VIRUS', False)

PAGINATE_THREADS_BY = getattr(settings, 'FORUM_PAGINATE_THREADS_BY', 16)
PAGINATE_REPLIES_BY = getattr(settings, 'FORUM_PAGINATE_REPLIES_BY', 12)
PAGINATE_MESSAGES_BY = getattr(settings, 'FORUM_PAGINATE_MESSAGES_BY', 20)

# maximum number of messages a unser can have in his message box
MESSAGE_BOX_SIZE = getattr(settings, 'FORUM_MESSAGE_BOX_SIZE', 40)

if CHECK_ATTACH_FOR_VIRUS:
    try:
        import pyclamd
    except ImportError:
        print('Option CHECK_ATTACH_FOR_VIRUS requires clamav and pyclamd installed.')
        exit()