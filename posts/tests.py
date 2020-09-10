import io

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from PIL import Image

from posts.models import Follow, Group, Post

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

        img = Image.new('1', (1, 1))
        image_io = io.BytesIO()
        img.save(image_io, 'JPEG')
        image_io.seek(0)
        img = image_io.read()

        self.default_image = SimpleUploadedFile(name='test_image.jpeg',
                                                content=img,
                                                content_type='image/jpeg')

    def tearDown(self):
        cache.clear()

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
        if paginator.count == 0:
            return None
        self.assertEqual(paginator.count, 1)
        return post_objects[0]

    def create_new_post(self, author=None, text=None,
                        group=None, image=None, commit=False):
        if author is None:
            author = self.user
        if text is None:
            text = self.default_text
        if group is None:
            group = self.default_group
        if image is None:
            image = self.default_image

        if commit:
            return Post.objects.create(
                author=author,
                text=text,
                group=group,
                image=image
            )
        else:
            return Post(author=author, text=text, group=group, image=image)

    def publish_new_post(self, post):
        response = self.client.post(
            reverse('new_post'),
            {'author': post.author, 'text': post.text, 'group': post.group.pk,
             'image': post.image},
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

        cache.clear()

        urls = [
            reverse('index'),
            reverse(
                'profile', kwargs={'username': self.user.username}
            ),
            reverse(
                'post',
                kwargs={'username': self.user.username, 'post_id': post.id}
            ),
        ]

        for url in urls:
            self.check_page_contains_post(url, post)

    def test_authorized_edit(self):

        post = self.create_new_post(commit=True)

        edited_text = 'edited_test_text'
        edited_group = Group.objects.create(
            title='edited_test_group',
            slug='edited_test_group',
            description='edited_test'
        )

        urls = [
            reverse('index'),
            reverse(
                'profile', kwargs={'username': self.user.username}
            ),
            reverse(
                'post',
                kwargs={'username': self.user.username, 'post_id': post.id}
            ),
            reverse(
                'group',
                kwargs={'slug': edited_group.slug}
            ),
        ]

        post_edit_url = reverse(
            'post_edit',
            kwargs={'username': self.user.username, 'post_id': post.id}
        )

        self.client.post(
            post_edit_url,
            {'text': edited_text, 'group': edited_group.pk},
            follow=True
        )

        edited_post = self.get_post_from_db(
            text=edited_text, group=edited_group.pk)
        self.assertNotEqual(edited_post, None)

        for url in urls:
            self.check_page_contains_post(url, edited_post)

    def test_pages_contain_image(self):
        post = self.create_new_post(commit=True)
        urls = [
            reverse('index'),
            reverse(
                'profile', kwargs={'username': self.user.username}
            ),
            reverse(
                'post',
                kwargs={'username': self.user.username, 'post_id': post.id}
            ),
            reverse(
                'group',
                kwargs={'slug': self.default_group.slug}
            ),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, '<img')

    def test_not_image_error(self):
        not_image = SimpleUploadedFile(
            name='test_not_image.txt',
            content=b'test_text'
        )
        post = self.create_new_post(image=not_image)
        response = self.publish_new_post(post)
        self.assertFormError(response, 'form', 'image',
                             errors='Загрузите правильное изображение. '
                                    'Файл, который вы загрузили, поврежден '
                                    'или не является изображением.')

    def test_cached_index_page(self):

        def create_post_and_check(text, should_exist):
            self.create_new_post(text=text, commit=True)
            response = self.client.get(reverse('index'))
            if should_exist:
                self.assertContains(response, text)
            else:
                self.assertNotContains(response, text)

        create_post_and_check('test_text_1', True)
        create_post_and_check('test_text_2', False)

        cache.clear()

        create_post_and_check('test_text_1', True)
        create_post_and_check('test_text_2', True)

    def follow_to_user(self, username):
        response = self.client.post(
            reverse('profile_follow',
                    kwargs={'username': username}),
            follow=True)
        self.assertEqual(response.status_code, 200)

    def test_user_follow_unfollow(self):
        author = User.objects.create_user(username='author')

        def test_using_post_method():
            self.follow_to_user(author.username)
            self.assertEqual(self.user.follower.count(), 1)

            response = self.client.post(
                reverse('profile_unfollow',
                        kwargs={'username': author.username}),
                follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(self.user.follower.count(), 0)

        # Для ревьюера. В чатике увидел подбные варианты,
        # мне они не кажутся правильными, но я на всякий случай пока оставлю.
        # После первого ревью все комменты почищу.
        def test_using_database():
            Follow.objects.create(user=self.user, author=author)
            self.assertEqual(self.user.follower.count(), 1)

            Follow.objects.filter(user=self.user, author=author).delete()
            self.assertEqual(self.user.follower.count(), 0)

        test_using_post_method()
        # test_using_database()

    def test_user_follow_index(self):
        followed_user = User.objects.create_user(username='followed_user')
        unfollowed_user = User.objects.create_user(username='unfollowed_user')
        author = User.objects.create_user(username='author')

        new_post = self.create_new_post(author=author, commit=True)

        self.client.force_login(followed_user)
        self.follow_to_user(author.username)

        tested_post = self.get_post_from_page(reverse('follow_index'))
        self.compare_posts(new_post, tested_post)

        self.client.force_login(unfollowed_user)
        tested_post = self.get_post_from_page(reverse('follow_index'))
        self.assertEqual(tested_post, None)

    def test_comment(self):
        post = self.create_new_post(commit=True)

        def add_comment():
            response = self.client.post(
                reverse('add_comment',
                        kwargs={'username': self.user.username,
                                'post_id': post.id}), {'text': 'comment_text'},
                follow=True)
            self.assertEqual(response.status_code, 200)
            return response

        add_comment()
        self.assertEqual(post.comments.count(), 1)

        self.client.logout()
        post.comments.filter(text='comment_text').delete()
        add_comment()
        self.assertEqual(post.comments.count(), 0)
