#-*- coding:utf-8 -*-
from django.views.generic.dates import _get_next_prev_month

from app_settings import *

from models import MessageBox
from models import Category
from models import Forum
from models import Thread
from models import Profile
from models import Rating
from models import FLAG_NEW, FLAG_READEN

from forms import ReplyForm, ThreadForm
from forms import ProfileForm, RateForm
from forms import MessageForm

from django.db import transaction
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.views.generic import TemplateView, DetailView, ListView, View
from django.http import HttpResponse

from django.shortcuts import get_object_or_404 as get_object
from django.shortcuts import render_to_response, render, redirect

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.utils import simplejson as json


def request_profile(function=None, ensure=False):
    def decorator(function):
        def inner_decorator(request, *args, **kwargs):
            try:
                request.profile = Profile.objects.get(pk=request.user.id)
            except Profile.DoesNotExist:
                if ensure:
                    messages.warning(request, _('Please, create your profile before continuing.'))
                    return redirect(''.join([reverse('forum:edit_profile'), '?next=', request.path]))
            return function(request, *args, **kwargs)

        return inner_decorator

    if function is None:
        return decorator
    else:
        return decorator(function)


@request_profile
def index_view(request):
    return render(request, 'forum/index.html', {
        'category_set': Category.objects.active()
    })


@request_profile
def public_profile_view(request, nickname):
    return render(request, 'forum/profile.html', {
        'is_self': False,
        'profile': get_object(Profile, nickname=nickname)
    })


@login_required
@request_profile(ensure=True)
def profile_view(request):
    return render(request, 'forum/profile.html', {
        'is_self': True,
        'profile': request.profile
    })


@login_required
@request_profile
def edit_profile_view(request):
    try:
        profile = Profile.objects.get(pk=request.user.id)
    except Profile.DoesNotExist:
        profile = None

    form = ProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=profile)

    if form.is_bound and form.is_valid():
        form.save(request.user)
        messages.info(request, _('Profile updated successfully'))

        # just like login, forum:profile accepts a next redirect parameter
        next_page = request.GET.get('next') or 'forum:profile'
        return redirect(next_page)

    return render(request, 'forum/edit_profile.html', {
        'form': form,
        'profile': profile
    })


@login_required
@request_profile(ensure=True)
def send_message_view(request, nickname):
    recipient = get_object(Profile, nickname=nickname)
    form = MessageForm(request.POST or None)

    if form.is_bound and form.is_valid():
        form.save(request.profile, recipient)
        return redirect(recipient)

    return render(request, 'forum/send_message.html', {
        'profile': request.profile,
        'recipient': recipient,
        'form': form
    })


@login_required
@request_profile(ensure=True)
def messages_view(request, pk_message=None):
    message_box, created = MessageBox.objects.get_or_create(profile=request.profile)
    messages = request.profile.messages.active()

    if pk_message:
        message = get_object(messages, pk=pk_message)
        return render(request, 'forum/message.html', {'message': message})
    else:
        number_of_messages = messages.count()
        number_of_new_messages = messages.filter(was_read=False).count()
        page_number = request.GET.get('page', 1)
        paginator = Paginator(messages, 12)
        object_list = paginator.page(page_number)
        return render(request, 'forum/messages.html', {
            'profile': request.profile,
            'object_list': object_list,
            'number_of_messages': number_of_messages,
            'number_of_new_messages': number_of_new_messages
        })


def category_view(request, pk_category):
    category_set = Category.objects.active().filter(pk=pk_category)
    return render(request, 'forum/index.html', {'category_set': category_set})


def forum_view(request, pk_forum):
    forum = get_object(Forum.objects.active(), pk=pk_forum)
    category = forum.category
    threads = forum.threads.active()
    page_number = request.GET.get('page', 1)
    object_list = Paginator(threads, PAGINATE_THREADS_BY).page(page_number)
    return render(request, 'forum/forum.html', {
        'category': category,
        'forum': forum,
        'object_list': object_list
    })


def thread_view(request,  pk_forum,  pk_thread):
    forum = get_object(Forum.objects.active(), pk=pk_forum)
    category = forum.category
    threads = forum.threads.active()
    thread = get_object(threads,  pk=pk_thread)
    replies = thread.replies.active()
    page_number = request.GET.get('page', 1)
    object_list = Paginator(replies, PAGINATE_REPLIES_BY).page(page_number)

    if ALLOW_INLINE_REPLY:
        form = ReplyForm(request.POST or None)

        if form.is_bound and form.is_valid():
            new_reply = form.save()
            return redirect(new_reply)

    thread.update_views(request)
    return render(request,  'forum/thread.html',  {
            'category': category,
            'form': form,
            'forum': forum,
            'thread': thread,
            'object_list': object_list
        })


@login_required
@request_profile(ensure=True)
@transaction.commit_on_success
def new_thread_view(request, pk_forum, pk_thread=None):
    forum = get_object(Forum.objects.active(), pk=pk_forum)
    category = forum.category

    thread_form = ThreadForm(
        request.POST or None,
        request.method == 'POST' and request.FILES or None)
    reply_form = ReplyForm(
        request.POST or None,
        request.method == 'POST' and request.FILES or None)

    if thread_form.is_bound and reply_form.is_bound \
       and thread_form.is_valid() and reply_form.is_valid():

        new_thread = thread_form.save(request.profile, forum)
        reply_form.save(request.profile, forum, new_thread)
        return redirect(new_thread)
    return render(request, 'forum/new_thread.html', {
            'category': category,
            'forum': forum,
            'thread_form': thread_form,
            'reply_form': reply_form
        })


@login_required
@request_profile(ensure=True)
@transaction.commit_on_success
def reply_view(request, pk_forum,  pk_thread):
    forum = get_object(Forum.objects.active(), pk=pk_forum)
    category = forum.category
    threads = forum.threads.active()
    thread = get_object(threads,  pk=pk_thread)
    form = ReplyForm(request.POST or None)

    if form.is_bound and form.is_valid():
        new_reply = form.save(request.profile, forum, thread)
        return redirect(new_reply)

    return render(request, 'forum/reply.html', {
        'category': category,
        'forum': forum,
        'thread': thread,
        'form': form
    })


@login_required
@request_profile(ensure=True)
def rate_reply_view(request, pk_forum,  pk_thread, pk_reply):
    forum = get_object(Forum.objects.active(), pk=pk_forum)
    threads = forum.threads.active()
    thread = get_object(threads,  pk=pk_thread)
    reply = get_object(thread.replies.active(), pk=pk_reply)

    form = RateForm(request.POST or None)
    if form.is_bound and form.is_valid():
        rating = form.save(request.profile, reply)
        return HttpResponse(
            json.dumps({'status':'ok', 'message': 'success'}),
            mimetype='application/json')

    return HttpResponse(
        json.dumps({'status':'error', 'message': 'invalid form data'}),
        mimetype='application/json')