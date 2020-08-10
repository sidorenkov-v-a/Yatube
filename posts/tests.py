from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from posts.models import Post
User = get_user_model()


class PostsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="test_user",
            email="test_usesr@test_usesr.com",
            password="test_user_pass"
        )

    def get_context(self, response, key):
        self.assertTrue(
            key in response.context,
            msg=f'response context does not contain key: {key}'
        )
        return response.context[key]

    def login(self, user_name, password):
        self.assertTrue(
            self.client.login(username=user_name, password=password),
            msg='Cannot log in test_user'
        )

    def get_post_list(self, response):
        return self.get_context(response, 'page').object_list

    def test_profile(self):
        response = self.client.get("/test_user/")
        self.assertEqual(
            response.status_code, 200, msg='Check if /profile/ exist'
        )

    def test_authorized_new(self):
        # Try to log in
        self.login('test_user', 'test_user_pass')

        # Check if there are no posts yet
        response = self.client.get('/test_user/')
        self.assertTrue('page' in response.context)
        self.assertTrue(len(self.get_post_list(response)) == 0)

        # Try to create new post by authorized user
        response = self.client.post(
            '/new/', {'text': 'Authorized_test_text'}, follow=True
        )
        self.assertRedirects(
            response, '/',
            status_code=302, target_status_code=200,
            fetch_redirect_response=True,
            msg_prefix='Authorized users should be redirected to /'
        )

        # Check if there one just created post
        response = self.client.get('/test_user/')
        self.assertTrue('page' in response.context)
        self.assertTrue(len(self.get_post_list(response)) == 1)

    def test_unauthorized_new(self):
        self.client.logout()

        # Save posts amount before
        response = self.client.get('/')
        self.assertTrue('page' in response.context)
        post_amount = len(self.get_post_list(response))

        # Try to create new post
        response = self.client.post(
            '/new/', {'text': 'Unauthorized_test_text'}, follow=True
        )
        self.assertRedirects(
            response, '/auth/login/?next=/new/',
            status_code=302, target_status_code=200,
            fetch_redirect_response=True,
            msg_prefix='Unauthorized has not been redirected to /auth/login/'
        )

        # Check posts amount after
        response = self.client.get('/')
        self.assertTrue('page' in response.context)
        new_post_amount = len(self.get_post_list(response))
        self.assertEqual(
            post_amount, new_post_amount,
            msg='Amount of posts should be the same.'
        )

    def test_published_post(self):
        self.login('test_user', 'test_user_pass')

        # Save posts amount before
        response = self.client.get('/')
        index_post_amount = len(self.get_post_list(response))

        response = self.client.get('/test_user/')
        profile_post_amount = len(self.get_post_list(response))

        # Create new post
        response = self.client.post(
            '/new/', {'text': 'test_text'}, follow=True
        )
        post_id = Post.objects.get(text='test_text', author=self.user).id

        # Check post amount and id for index page
        response = self.client.get('/')
        new_index_post_amount = len(self.get_post_list(response))
        new_post_id = self.get_post_list(response)[0].id

        self.assertEqual(
            post_id, new_post_id,
            msg='Newest post id in index page should be the same'
        )
        self.assertTrue(index_post_amount + 1 == new_index_post_amount)

        # Check post amount and id for profile page
        response = self.client.get('/test_user/')
        new_profile_post_amount = len(self.get_post_list(response))
        new_post_id = self.get_post_list(response)[0].id

        self.assertEqual(
            post_id, new_post_id,
            msg='Newest post id in index page should be the same'
        )
        self.assertTrue(profile_post_amount + 1 == new_profile_post_amount)

        # Check post page
        response = self.client.get(f'/test_user/{post_id}/')
        self.assertEqual(
            response.status_code, 200,
            msg=f'Where post page? /test_user/{post_id}/'
        )
        post = self.get_context(response, 'post')
        self.assertTrue(post is not None)
        self.assertTrue(post.id == post_id)

    def test_authorized_edit(self):
        self.login('test_user', 'test_user_pass')

        text = 'test_authorized_edit_text'
        self.client.post('/new/', {'text': text}, follow=True)

        post_id = Post.objects.get(text=text, author=self.user).id
        new_text = 'new_test_authorized_edit_text'

        response = self.client.post(
            f'/test_user/{post_id}/edit/',
            {'text': new_text},
            follow=True
        )
        self.assertRedirects(
            response, f'/test_user/{post_id}/',
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )

        response = self.client.get('/')
        edited_text = self.get_post_list(response)[0].text
        self.assertEqual(new_text, edited_text, msg='Text should be edited')

        response = self.client.get('/test_user/')
        edited_text = self.get_post_list(response)[0].text
        self.assertEqual(new_text, edited_text, msg='Text should be edited')

        response = self.client.get(f'/test_user/{post_id}/')
        edited_text = self.get_context(response, 'post').text
        self.assertEqual(new_text, edited_text, msg='Text should be edited')
