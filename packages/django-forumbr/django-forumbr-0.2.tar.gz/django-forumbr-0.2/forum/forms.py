# -*- coding:utf-8 -*-

from app_settings import *
from validators import max_upload_size, virus_check
from models import Reply, Thread, Profile, Message, Rating

from django import forms
from django.utils.translation import ugettext_lazy as _

THREAD_META_FIELDS = ['title']

if THREAD_ALLOW_IMAGE:
    THREAD_META_FIELDS.append('image')
if THREAD_ALLOW_ATTACHMENT:
    THREAD_META_FIELDS.append('attachment')


class MessageForm(forms.ModelForm):

    def __init__(self, *args, **kw):
        super(MessageForm, self).__init__(*args, **kw)
        self.fields['message'].required = True

    def save(self, author, recipient, commit=True):
        message = super(MessageForm, self).save(commit=False)
        message.author = author
        message.to = recipient

        if commit:
            message.save()

        return message

    class Meta:
        model = Message
        fields = ['title', 'message']


class ReplyForm(forms.ModelForm):
    """
    Form used to create a reply
    """

    class Meta:
        model = Reply
        fields = ['message']

    def __init__(self, *args, **kw):
        super(ReplyForm, self).__init__(*args, **kw)
        self.fields['message'].required = True

    def save(self, author, forum, thread, commit=True):
        reply = super(ReplyForm, self).save(commit=False)
        reply.author = author
        reply.forum = forum
        reply.thread = thread

        if commit:
            reply.save()

        return reply


class ThreadForm(forms.ModelForm):
    if THREAD_ALLOW_IMAGE:
        __field = Thread._meta.get_field('image')
        image = forms.ImageField(
            label = unicode(__field.verbose_name),
            help_text = unicode(__field.help_text),
            validators = [max_upload_size(MAX_THREAD_IMAGE_SIZE)],
            required = not __field.blank
        )

    if THREAD_ALLOW_ATTACHMENT:
        __field = Thread._meta.get_field('attachment')
        attachment = forms.FileField(
            label = unicode(__field.verbose_name),
            help_text = unicode(__field.help_text),
            validators = [max_upload_size(MAX_THREAD_ATTACH_SIZE), virus_check],
            required = not __field.blank
        )

    class Meta:
        model = Thread
        fields = THREAD_META_FIELDS

    def save(self, author, forum, commit=True):
        thread = super(ThreadForm, self).save(commit=False)
        thread.author = author
        thread.forum = forum

        if commit:
            thread.save()

        return thread


class ProfileAdminForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ['flag']


class ProfileForm(forms.ModelForm):
    message = forms.CharField(label=_('Signature'), widget=forms.Textarea, required=False)
    avatar = forms.ImageField(
        label=Profile._meta.get_field('avatar').verbose_name.title(),
        validators=[max_upload_size(AVATAR_MAX_SIZE)],
    )

    class Meta:
        model = Profile
        fields = ['gender', 'nickname', 'avatar', 'message']
        exclude = ['user', 'flag', 'reputation', 'threads_counter', 'replies_counter']

    def save(self, user, commit=True):
        profile = super(ProfileForm, self).save(commit=False)
        profile.user = user

        if commit:
            profile.save()

        return profile


class RateForm(forms.ModelForm):
    def save(self, author, reply, **kw):
        self.author = author
        self.reply = reply
        return super(RateForm, self).save(**kw)

    class Meta:
        model = Rating