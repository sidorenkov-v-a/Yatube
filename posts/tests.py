from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

import os

User = get_user_model()


class PostsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='test_user',
        )
        self.client.force_login(self.user)

        self.default_group = Group.objects.create(
            title='test_group',
            slug='test_group',
            description='test'
        )
        self.default_text = 'test_text'

    def get_context(self, response, key):
        self.assertTrue(
            key in response.context,
            msg=f'response context does not contains the key: {key}'
        )
        return response.context[key]

    def get_post_from_page(self, url):
        response = self.client.get(url)
        if 'page' in response.context:
            return self.get_post_from_paginator(response)
        else:
            return self.get_context(response, 'post')

    def get_post_from_paginator(self, response):
        post_objects = self.get_context(response, 'page').object_list
        paginator = self.get_context(response, 'paginator')
        self.assertEqual(paginator.count, 1)
        return post_objects[0]

    def create_new_post(self, author=None, text=None,
                        group=None, commit=False):
        if author is None:
            author = self.user
        if text is None:
            text = self.default_text
        if group is None:
            group = self.default_group

        if commit:
            return Post.objects.create(author=author, text=text, group=group)
        else:
            return Post(author=author, text=text, group=group)

    def publish_new_post(self, post):
        response = self.client.post(
            reverse('new_post'),
            {'author': post.author, 'text': post.text, 'group': post.group.pk},
            follow=True
        )
        self.assertEqual(
            response.status_code,
            200,
            msg='can not publish the post'
        )
        return response

    def check_page_contains_post(self, url, created_post):
        post = self.get_post_from_page(url)
        self.compare_posts(created_post, post)

    def check_redirect(self, response, target_url):
        self.assertRedirects(
            response,
            target_url,
            fetch_redirect_response=True,
            msg_prefix=f'Authorized users should be redirected to {target_url}'
        )

    def get_post_from_db(self, author=None, text=None, group=None):
        if author is None:
            author = self.user
        if text is None:
            text = self.default_text
        if group is None:
            group = self.default_group.pk
        return Post.objects.filter(
            text=text, author=author, group=group).first()

    def compare_posts(self, lhs, rhs):
        self.assertEqual(lhs.text, rhs.text, msg='posts have different text')
        self.assertEqual(lhs.group, rhs.group,
                         msg='posts have different group')
        self.assertEqual(lhs.author, rhs.author,
                         msg='posts have different author')

    def test_profile(self):
        profile_url = reverse(
            'profile', kwargs={'username': self.user.username})
        response = self.client.get(profile_url)

        self.assertEqual(
            response.status_code, 200, msg=f'{profile_url} does not exist'
        )

    def test_authorized_new(self):

        new_post = self.create_new_post()
        self.publish_new_post(new_post)

        posts_amount = Post.objects.count()
        self.assertEqual(posts_amount, 1)

        created_post = self.get_post_from_db()
        self.assertNotEqual(created_post, None)
        self.compare_posts(new_post, created_post)

    def test_unauthorized_new(self):
        self.client.logout()

        posts_amount = Post.objects.count()

        new_post = self.create_new_post()
        response = self.publish_new_post(new_post)

        new_posts_amount = Post.objects.count()
        self.assertEqual(posts_amount, new_posts_amount)

        need_login_url = f"{reverse('login')}?next={reverse('new_post')}"
        self.check_redirect(response, need_login_url)

        created_post = self.get_post_from_db()
        self.assertEqual(created_post, None)

    def test_published_post(self):

        post = self.create_new_post(commit=True)

        index_url = reverse('index')
        profile_url = reverse(
            'profile', kwargs={'username': self.user.username})
        post_url = reverse(
            'post',
            kwargs={'username': self.user.username, 'post_id': post.id})

        self.check_page_contains_post(index_url, post)
        self.check_page_contains_post(profile_url, post)
        self.check_page_contains_post(post_url, post)

    def test_authorized_edit(self):

        post = self.create_new_post(commit=True)

        edited_text = 'edited_test_text'
        edited_group = Group.objects.create(
            title='edited_test_group',
            slug='edited_test_group',
            description='edited_test'
        )

        index_url = reverse('index')

        profile_url = reverse(
            'profile', kwargs={'username': self.user.username})

        post_edit_url = reverse(
            'post_edit',
            kwargs={'username': self.user.username, 'post_id': post.id}
        )

        post_url = reverse(
            'post',
            kwargs={'username': self.user.username, 'post_id': post.id}
        )

        group_url = reverse(
            'group',
            kwargs={'slug': edited_group.slug}
        )

        self.client.post(
            post_edit_url,
            {'text': edited_text, 'group': edited_group.pk},
            follow=True
        )

        edited_post = self.get_post_from_db(
            text=edited_text, group=edited_group.pk)
        self.assertNotEqual(edited_post, None)

        self.check_page_contains_post(index_url, edited_post)
        self.check_page_contains_post(profile_url, edited_post)
        self.check_page_contains_post(post_url, edited_post)
        self.check_page_contains_post(group_url, edited_post)

    def test_pages_contain_image(self):
        self.assertTrue(os.path.exists('media/test.jpg'), msg='Test image does not exist')
