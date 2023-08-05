# -*- coding:utf-8 -*-

from .constants import *
from .markup import render_markup
from .validators import *
from .exceptions import *

from app_settings import *

from django.conf import settings
from django.db import models
from django.db.models import Sum, Count
from django.db.models.signals import pre_save, post_save, post_delete
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.template.defaultfilters import filesizeformat
from django.core.urlresolvers import reverse

import os
import datetime
from urlparse import urljoin

#from .model_fields import RestrictedFileField, RestrictedImageField

def forum_profile_for(user):
    instance, created = Profile.objects.get_or_create(user=user)
    return instance

# --- Custom managers
class ActiveManager(models.Manager):

    def active(self):
        return super(ActiveManager, self).filter(is_active=True)


# --- Abstract classes
class DatedModel(models.Model):
    creation_time = models.DateTimeField(auto_now_add=True)
    modification_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ActiveModel(models.Model):
    is_active = models.BooleanField(verbose_name='Is active?', default=True)
    objects = ActiveManager()

    class Meta:
        abstract = True


class MessageModel(models.Model):
    """
    Used for models that should have a formatted message attached.
    """
    message = models.TextField(blank=True, null=True)
    message_format = models.IntegerField(choices=MARKUP_CHOICES, default=TRANSLATE_MARKUP[MARKUP])
    html = models.TextField(editable=False, blank=True, null=True)

    class Meta:
        abstract = True

# --- End abstract classes

class Profile(DatedModel, ActiveModel, MessageModel):
    """
    Forum user profile
    """
    user = models.OneToOneField(User, related_name="forum_profile", primary_key=True)
    nickname = models.SlugField(max_length=50, unique=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    avatar = models.ImageField(
        verbose_name=_('Avatar image'),
        help_text=_('Up to %s') % filesizeformat(AVATAR_MAX_SIZE),
        upload_to='forum/avatar/uploads/', blank=True, null=True)
    flag = models.IntegerField(default=0, help_text=_('System wise attribute'))

    reputation = models.PositiveIntegerField(default=0)
    threads_counter = models.PositiveIntegerField(default=0)
    replies_counter = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'forum_profile'
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
        ordering = ['-creation_time']

    def __unicode__(self):
        return unicode(self.user)

    @models.permalink
    def get_absolute_url(self):
        return 'forum:profile', [self.nickname]

    def set_flag(self, flag):
        self.flag = self.flag|flag

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return settings.STATIC_URL + "img/forum/avatar/dull_face.png"

    def update_threads_counter(self):
        self.threads_counter = self.threads.count()

    def update_replies_counter(self):
        self.replies_counter = self.replies.count()


class Category(DatedModel, ActiveModel):
    """
    Used to sort the forum
    """
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True, primary_key=True)

    class Meta:
        db_table = 'forum_category'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['slug']

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return 'forum:category', (self.slug,)


class Forum(DatedModel, ActiveModel):
    category = models.ForeignKey(Category, related_name='forum_set', help_text='Set to show forum in the index page', blank=True, null=True)
    parent = models.ForeignKey('self', related_name='children', blank=True, null=True, default=None)
    name = models.CharField(verbose_name=_("Forum name"), max_length=100)
    description = models.CharField(verbose_name=_("Description"), max_length=255, blank=True, null=True)
    moderation = models.ManyToManyField('Profile', related_name="moderation", blank=True, null=True)
    last_thread = models.OneToOneField('Thread', related_name="as_last_thread_for", blank=True, null=True, editable=False)

    threads_counter = models.PositiveIntegerField(_("Threads counter"), default=0, editable=False)
    replies_counter = models.PositiveIntegerField(_("Replies counter"), default=0, editable=False)

    class Meta:
        db_table = 'forum'
        verbose_name = 'Forum'
        verbose_name_plural = 'Forums'
        ordering = ['-creation_time']

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return 'forum:expose', [self.id]

    def parent_tree(self):
        parent_list = []
        parent = self.parent

        while parent is not None:
            parent_list.append(parent)
            parent = parent.parent

        return parent_list

    def latest_thread(self):
        try:
            return self.threads.active().latest('creation_time')
        except Thread.DoesNotExist:
            return None

    def check_permission(self, request):
        if self.access_filter == PERMISSION_LOGGED and not request.user.is_authenticated():
            raise LoginRequiredException()

    def update_threads_counter(self):
        self.threads_counter = self.threads.count()

    def update_replies_counter(self):
        agg = self.threads.aggregate(Sum('replies_counter'))
        self.replies_counter = agg['replies_counter__sum']


class Thread(DatedModel, ActiveModel):
    _order_by = ('title', 'author', 'replies_counter', 'view_counter')

    author = models.ForeignKey(Profile, related_name='threads')
    forum = models.ForeignKey(Forum, related_name='threads')
    status = models.IntegerField(choices=THREAD_STATUS_CH, default=THREAD_STATUS_OPEN)
    title = models.CharField(verbose_name=_('Title'), max_length=255)
    image = models.ImageField(verbose_name=_('Head image'), help_text='Shown at the thread top',
        #validators=[max_upload_size(MAX_THREAD_IMAGE_SIZE)],
        upload_to='uploads/forum/thread/image/',
        blank=True, null=True)
    attachment = models.FileField(verbose_name=_('Attachment'),
        help_text='Associate a file with this thread',
        #validators=[max_upload_size(MAX_THREAD_ATTACH_SIZE), virus_check],
        upload_to='forum/threads/attachment/',
        blank=True, null=True)

    views_counter = models.PositiveIntegerField(_("Views counter"), default=0, editable=False)
    replies_counter = models.PositiveIntegerField(_("Replies counter"), default=0, editable=False)
    authors_counter = models.PositiveIntegerField(_("Authors counter"), default=0, editable=False)

    class Meta:
        db_table = 'forum_thread'
        verbose_name = ugettext('Thread')
        verbose_name_plural = ugettext('Threads')
        ordering = ['-creation_time']

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return 'forum:thread', (self.forum_id, self.id), {}

    def get_attach_basename(self):
        return os.path.basename(self.attach.name)

    def update_views(self, request):
        """
        Updates the thread visit counter
        """
        ip_address = request.META['REMOTE_ADDR']
        return Views.objects.get_or_create(
            thread=self, ip_address=ip_address,
            date=datetime.date.today())

    def update_views_counter(self):
        self.views_counter = self.views.count()

    def update_replies_counter(self):
        self.replies_counter = self.replies.active().count()

    def update_authors_counter(self):
        agg = self.replies.active().aggregate(Count('author'))
        self.authors_counter = agg['author__count']


class Reply(DatedModel, ActiveModel, MessageModel):
    author = models.ForeignKey(Profile, related_name='replies')
    forum = models.ForeignKey(Forum, related_name='replies')
    thread = models.ForeignKey(Thread, related_name='replies')
    avg_rating = models.PositiveIntegerField(_('Average rating'), default=0)

    class Meta:
        db_table = 'forum_reply'
        verbose_name = ugettext('Reply')
        verbose_name_plural = ugettext('Replies')
        ordering = ['creation_time']

    def get_absolute_url(self):
        replies = self.thread.replies.active()
        page = int(list(replies).index(self) / PAGINATE_THREADS_BY)+1
        return "%s?page=%d" % (reverse('forum:thread', args=[self.forum.id, self.thread.id]), page)

    def update_reputation(self):
        agg = self.rating.aggregate(Sum('value'))
        self.reputation = agg['value__sum']


class Views(models.Model):
    date = models.DateField(auto_now_add=True)
    thread = models.ForeignKey(Thread, related_name='views')
    ip_address = models.IPAddressField()

    class Meta:
        db_table = 'forum_views'
        verbose_name = ugettext('View')
        verbose_name_plural = ugettext('Views')
        ordering = ('-date', '-thread')
        unique_together = ('thread', 'ip_address', 'date')

    def __unicode__(self):
        return "%s" % self.ip_address


class Rating(DatedModel):
    """
    Stores a pontuation given from an user for a reply. This is used
    to calculate the total reputation of the user
    """
    reply = models.ForeignKey(Reply, related_name='rating')
    author = models.ForeignKey(Profile, related_name='ratings')
    value = models.IntegerField(choices=RATING_CHOICES)

    class Meta:
        db_table='forum_rating'
        verbose_name = 'Rating'
        verbose_name_plural = 'Ratings'

    def __unicode__(self):
        return self.get_value_display()


class AbuseReport(DatedModel):
    """
    An logged user can report a reply for abuse.
    """
    reply = models.ForeignKey(Reply, related_name='reports')
    author = models.ForeignKey('Profile', related_name='abuse_reports')
    reason = models.IntegerField(choices=REASON_CH)
    observation = models.TextField(_('Any observations?'), blank=True, help_text=_('Use plain text'))

    class Meta:
        db_table = 'forum_abuse_report'
        verbose_name = ugettext('Abuse report')
        verbose_name_plural = ugettext('Abuse reports')

    def __unicode__(self):
        return len(self.observation) > 30 and (self.observation[:30] + '...') or self.get_reason_display()


class Subscription(DatedModel, ActiveModel):
    """
    Represents a subscription of an user to a thread. That means a user
    is interested in the subscribed thread and wish to follow updates on it.
    """
    profile = models.ForeignKey('Profile', related_name="forum_subscribes")
    thread = models.ForeignKey(Thread, related_name="subscriptions")

    class Meta:
        db_table = 'forum_subscription'
        verbose_name = ugettext('Subscription')
        verbose_name_plural = ugettext('subscriptions')
        unique_together = ('profile', 'thread')

    def __unicode__(self):
        return _("Subscription to thread %s") % self.thread


class MessageBox(DatedModel):
    profile = models.OneToOneField(Profile, related_name='message_box')
    box_size = models.PositiveIntegerField(default=20)

    class Meta:
        db_table = 'forum_message_box'
        verbose_name = _('Message box')
        verbose_name_plural = _('Message boxes')


class Message(DatedModel, ActiveModel, MessageModel):
    """
    Represents a private message sent from an user to another.
    """
    was_read = models.BooleanField(verbose_name=_('Was read?'), default=False)
    was_read_at = models.DateTimeField(editable=False, blank=True, null=True)
    author = models.ForeignKey(Profile, verbose_name=_('Author'), related_name='sent_messages')
    to = models.ForeignKey(Profile, verbose_name=_('Recipient'), related_name='messages')
    title = models.CharField(max_length=100)

    class Meta:
        db_table = 'forum_message'
        verbose_name = ugettext('Message')
        verbose_name_plural = ugettext('Messages')
        ordering = ['creation_time']

    @models.permalink
    def get_absolute_url(self):
        return 'forum:message', (), {'message_id':self.id}

    def __unicode__(self):
        return self.title


def on_new_profile(sender, instance, **kw):
    if kw.get('created'):
        MessageBox.objects.create(profile=instance)


post_save.connect(on_new_profile, sender=Profile,
    dispatch_uid='forum_post_save_on_new_profile')


def on_new_views(sender, instance, **kw):
    """
    Updates the view counter for a thread
    """
    if kw.get('created', True):
        instance.thread.update_views_counter()
        instance.thread.save()


post_save.connect(on_new_views, sender=Views,
    dispatch_uid='forum_post_save_on_new_views')


def on_new_thread(sender, instance, **kw):
    """
    Updates the threads_counter for the forum and thread author
    """
    # works for create and delete
    if kw.get('created', True) is True:
        instance.forum.update_threads_counter()
        instance.forum.save()

        instance.author.update_threads_counter()
        instance.author.save()


post_save.connect(on_new_thread, sender=Thread,
    dispatch_uid='forum_thread_post_save_update_threads_counter')
post_delete.connect(on_new_thread, sender=Thread,
    dispatch_uid='forum_thread_post_delete_update_threads_counter')


def on_new_rating(sender, instance, **kw):
    """
    Updates rating counter of the reply.
    """
    # works for create and delete
    if kw.get('created', True) is True:
        instance.reply.update_reputation()
        instance.reply.save()


post_save.connect(on_new_rating, sender=Rating,
    dispatch_uid='forum_post_save_on_new_rating')
post_delete.connect(on_new_rating, sender=Rating,
    dispatch_uid='forum_post_delete_on_new_rating')


def on_new_reply(sender, instance, **kw):
    """
    Actually this method name is misleading. The counters that are
    updated are, actually, the counters of the thread this reply is
    related to.
    """
    if kw.get('created', True) is True:
        instance.thread.update_authors_counter()
        instance.thread.update_replies_counter()
        instance.thread.save()

        # update reply counter for the author
        instance.author.update_replies_counter()
        instance.author.save()

        # sum all attributes replies_counter of all threads and updates forum
        instance.thread.forum.update_replies_counter()
        instance.thread.forum.save()


post_save.connect(on_new_reply, sender=Reply,
    dispatch_uid='forum_post_save_on_new_reply')
post_delete.connect(on_new_reply, sender=Reply,
    dispatch_uid='forum_post_delete_on_new_reply')


def update_html(sender, instance, *args, **kw):
    """
    pre_save event
    Renders the html for a reply and stores it in an attribute for
    performance
    """
    instance.html = render_markup(instance.message_format, instance.message)


pre_save.connect(update_html, sender=Profile,
    dispatch_uid='forum_pre_save_update_profile_html')
pre_save.connect(update_html, sender=Reply,
    dispatch_uid='forum_pre_save_update_reply_html')
pre_save.connect(update_html, sender=Message,
    dispatch_uid='forum_pre_save_update_message_html')
