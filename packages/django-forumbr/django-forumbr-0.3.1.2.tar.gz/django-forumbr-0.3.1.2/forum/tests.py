# -*- coding:utf-8 -*-
"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from random import randint
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.contrib.auth.models import User


def new_user(username='john', email='email@email.com', password='doe'):
    return User.objects.create_user(username, email, password)


def new_profile(user, nickname=None, gender=None):
    from forum.models import Profile, GENDER_MALE

    return Profile.objects.create(
        user=user,
        nickname=nickname or user.username,
        gender=gender or GENDER_MALE)


class TestUrlBuild(TestCase):
    """
    Testa se todas as ulrs definidas em urls.py são geradas corretamente
    para os argumentos corretos e geram exceção para argumentos incorretos.
    """
    slug = 'aAbBcCdDeE_-0123456789'
    object_id = 12345

    def test_index(self):
        reverse('forum:index')

    def test_view_profile(self):
        reverse('forum:profile')

    def test_view_public_profile(self):
        reverse('forum:profile', args=[self.slug])

    def test_edit_profile(self):
        reverse('forum:edit_profile')

    def test_view_messages(self):
        reverse('forum:messages')

    def test_view_message(self):
        reverse('forum:messages', args=[self.object_id])

    def test_view_send_message(self):
        reverse('forum:send_message', args=[self.slug])

    def test_view_forum(self):
        reverse('forum:expose', args=[self.object_id])

    def test_view_forum_thread(self):
        reverse('forum:thread', args=[self.object_id, 432])

    def test_forum_new_thread(self):
        reverse('forum:new_thread', args=[self.object_id])

    def test_forum_reply(self):
        reverse('forum:reply', args=[self.object_id, 432])



class TestIndexVew(TestCase):
    url = reverse('forum:index')
    template = 'forum/index.html'

    def test_access_without_user_account(self):
        resp = self.client.get(self.url)
        self.assertTemplateUsed(resp, self.template)

    def test_access_without_profile(self):
        resp = self.client.get(self.url)
        self.assertTemplateUsed(resp, self.template)

    def test_access_with_profile(self):
        resp = self.client.get(self.url)
        self.assertTemplateUsed(resp, self.template)


class TestProfileView(TestCase):
    url = reverse('forum:profile')
    template = 'forum/profile.html'

    def test_access_without_user_account(self):
        resp = self.client.get(self.url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + self.url)

    def test_access_without_profile(self):
        User.objects.create_user('john', 'email@email.com', 'doe')
        self.client.login(username='john', password='doe')

        resp = self.client.get(self.url)
        self.assertRedirects(resp, reverse('forum:edit_profile') + '?next=' + self.url)

    def test_access_with_profile(self):
        from forum.models import Profile

        user = User.objects.create_user('john', 'email@email.com', 'doe')
        Profile.objects.create(user=user, nickname='blah')
        self.client.login(username='john', password='doe')

        resp = self.client.get(self.url)
        self.assertTemplateUsed(resp, self.template)


class TestPublicProfileView(TestCase):
    template = 'forum/profile.html'

    def test_access_without_user_account(self):
        from forum.models import Profile

        user = User.objects.create_user('john', 'email@email.com', 'doe')
        Profile.objects.create(user=user, nickname='blah')

        url = reverse('forum:profile', args=['blah'])
        resp = self.client.get(url)
        self.assertTemplateUsed(resp, self.template)


class TestEditProfileView(TestCase):
    def setUp(self):
        self.url = reverse('forum:edit_profile')

    def test_access_without_user_account(self):
        resp = self.client.get(self.url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + self.url)

    def test_access_without_profile(self):
        user = User.objects.create_user('john', 'email@email.com', 'doe')
        self.client.login(username='john', password='doe')

        resp = self.client.get(self.url)
        self.assertTemplateUsed(resp, 'forum/edit_profile.html')

    def test_access_with_profile(self):
        user = User.objects.create_user('john', 'email@email.com', 'doe')
        self.client.login(username='john', password='doe')

        resp = self.client.get(self.url)
        self.assertTemplateUsed(resp, 'forum/edit_profile.html')


class TestSendMessageView(TestCase):
    def setUp(self):
        self.john = new_user()
        self.john_profile = new_profile(self.john)

        self.maria = new_user(username='maria')
        self.maria_profile = new_profile(self.maria)

    def test_access_send_msg_page_to_non_existing_nickname(self):
        self.client.login(username=self.john.username, password='doe')
        resp = self.client.get(reverse('forum:send_message', args=['blabla']))
        self.assertEqual(resp.status_code, 404)


class TestMessagesView(TestCase):
    def setUp(self):
        self.url = reverse('forum:messages')

    def test_access_without_user_account(self):
        resp = self.client.get(self.url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + self.url)

    def test_access_without_profile(self):
        user = new_user()
        self.client.login(username='john', password='doe')

        resp = self.client.get(self.url)
        self.assertRedirects(resp, reverse('forum:edit_profile') + '?next=' + self.url)

    def test_access_with_profile(self):
        user = new_user()
        profile = new_profile(user)

        self.client.login(username='john', password='doe')
        resp = self.client.get(self.url)
        self.assertTemplateUsed(resp, template_name='forum/messages.html')

    def test_messages_are_there(self):
        from forum.models import Message, GENDER_FEMALE

        first_profile = new_profile(
            new_user(username='john', password='doe'))

        second_profile = new_profile(
            new_user(username='maria', password='clara'),
            gender=GENDER_FEMALE)

        Message.objects.create(
            author=first_profile,
            to=second_profile,
            title='test message',
            message='this is a test')

        # authenticating our user
        self.client.login(username='maria', password='clara')

        resp = self.client.get(self.url)
        self.assertContains(resp, 'test message')


class TestCategoryView(TestCase):
    def test_access_to_category_view_without_forum(self):
        from forum.models import Category

        name, slug = 'some category', 'some-category'
        category = Category.objects.create(name=name, slug=slug)
        url = reverse('forum:category', args=[slug])
        resp = self.client.get(url)
        self.assertTemplateUsed(resp, 'forum/index.html')

    def test_access_to_category_view_with_forum(self):
        from forum.models import Category

        name, slug = 'some category', 'some-category'
        category = Category.objects.create(name=name, slug=slug)
        url = reverse('forum:category', args=[slug])
        resp = self.client.get(url)
        self.assertTemplateUsed(resp, 'forum/index.html')


class TestForumView(TestCase):

    def test_access_to_non_existing_forum(self):
        from forum.models import Forum

        resp = self.client.get(reverse('forum:expose', args=[100]))
        self.assertEqual(resp.status_code, 404)

    def test_access_to_forum_view_without_user_account(self):
        from forum.models import Forum

        forum = Forum.objects.create(name='some name')
        resp = self.client.get(reverse('forum:expose', args=[forum.id]))
        self.assertTemplateUsed(resp, 'forum/forum.html')


class TestThreadView(TestCase):
    def setUp(self):
        from forum.models import Forum, Thread, Reply

        self.user = new_user()
        self.profile = new_profile(self.user)
        self.forum = Forum.objects.create(name='bla bla')
        self.thread = Thread.objects.create(
            forum=self.forum,
            author=self.profile,
            title='some title')
        self.reply = Reply.objects.create(
            author = self.profile,
            forum = self.forum,
            thread = self.thread,
            message = 'some message')

    def test_access_to_thread_view_without_user_account(self):
        resp = self.client.get(reverse('forum:thread',
            args=[self.forum.id, self.thread.id]))
        self.assertTemplateUsed(resp, 'forum/thread.html')

    def test_thread_title_content(self):
        resp = self.client.get(reverse('forum:thread',
            args=[self.forum.id, self.thread.id]))
        self.assertContains(resp, 'some title')

    def test_reply_message_content(self):
        resp = self.client.get(reverse('forum:thread',
            args=[self.forum.id, self.thread.id]))
        self.assertContains(resp, 'some message')


class TestReplyView(TestCase):
    pass