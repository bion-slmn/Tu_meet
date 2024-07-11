from django.test import TestCase
from rest_framework.test import APIClient
from social_app.models import (
    Post, Like, Comment, User)
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from PIL import Image
import tempfile, unittest
from django.test import TestCase
from django.test import override_settings
from unittest.mock import patch, MagicMock


def get_temporary_image():
    image = Image.new('RGB', (100, 100))
    tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
    image.save(tmp_file)
    tmp_file.seek(0)
    return tmp_file



class PostViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='12345', email='bion@gmail.com')
        image_file = SimpleUploadedFile(
            "sample.jpg",
            b"file_content",
            content_type="image/jpeg")
        self.post1 = Post.objects.create(
            content="Sample post content", user=self.user)
        self.post2 = Post.objects.create(
            content="Another sample post",
            user=self.user,
            pics=image_file)
        self.like = Like.objects.create(post=self.post1, user=self.user)
        self.comment = Comment.objects.create(
            content="Great post!", post=self.post1, user=self.user)
        self.response = self.client.get(reverse('all_posts'))
    def teardown(self):
        self.user.delete()

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_response_structure(self):

        self.assertEqual(self.response.status_code, 200)
        data = self.response.json()
        self.assertIn('count', data)
        self.assertIn('next', data)
        self.assertIn('previous', data)
        self.assertIn('results', data)
        self.assertIsInstance(data['results'], list)

    def test_post_content(self):
        self.assertEqual(self.response.status_code, 200)
        data = self.response.json()
        results = data['results']
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['content'], "Sample post content")
        self.assertEqual(results[1]['content'], "Another sample post")

    def test_post_picture(self):

        self.assertEqual(self.response.status_code, 200)
        data = self.response.json()
        results = data['results']
        self.assertEqual(len(results), 2)
        self.assertIsNone(results[0]['pics'])
        self.assertIsNotNone(results[1]['pics'])

    def test_post_id(self):

        self.assertEqual(self.response.status_code, 200)
        data = self.response.json()
        results = data['results']
        self.assertEqual(len(results), 2)
        self.assertIsNotNone(results[0]['id'])
        self.assertIsNotNone(results[1]['id'])

    def test_post_created_at(self):

        self.assertEqual(self.response.status_code, 200)
        data = self.response.json()
        results = data['results']
        self.assertEqual(len(results), 2)
        self.assertIsNotNone(results[0]['created_at'])
        self.assertIsNotNone(results[1]['created_at'])

    def test_post_user(self):

        self.assertEqual(self.response.status_code, 200)
        data = self.response.json()
        results = data['results']
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]['user']['username'], "testuser")
        self.assertEqual(results[1]['user']['username'], "testuser")

    def test_likes_count(self):
        self.response = self.client.get(reverse('all_posts'))
        self.assertEqual(self.response.status_code, 200)
        data = self.response.json()
        results = data['results']
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]['likes_count'], 1)
        self.assertEqual(results[1]['likes_count'], 0)

    def test_comments_count(self):
        self.response = self.client.get(reverse('all_posts'))
        self.assertEqual(self.response.status_code, 200)
        data = self.response.json()
        results = data['results']
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]['comments_count'], 1)
        self.assertEqual(results[1]['comments_count'], 0)


class PostDetailsTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass', email='bion@gmail.com')
        self.post = Post.objects.create(content="Test content", user=self.user)
        self.url = reverse('view_a_post', kwargs={'post_id': self.post.id})
        self.client.login(username='testuser', password='testpass')

    def tearDown(self):
        # Clean up after each test
        self.post.delete()
        self.user.delete()

    def test_get_post_details(self):

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('id', response.data)
        self.assertIn('created_at', response.data)
        self.assertIn('content', response.data)
        self.assertIn('pics', response.data)
        self.assertIn('username', response.data['user'])
        self.assertIn('likes_count', response.data)
        self.assertIn('comments_count', response.data)

    def test_content(self):
        response = self.client.get(self.url)
        self.assertEqual(response.data['content'], "Test content")
        self.assertIsNone(response.data['pics'])

    def test_likes_comment_count(self):
        response = self.client.get(self.url)
        self.assertEqual(response.data['likes_count'], 0)
        self.assertEqual(response.data['comments_count'], 0)

    def test_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.data['user']['username'], 'testuser')
        self.assertIsNotNone(response.data['user']['id'])



class CreatePostTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='john', password='password123', email='bion@gmail.com')
        self.client.login(username='john', password='password123')
        # Update this with the correct URL name
        self.url = reverse('create_post')
    def teardown(self):
        User.objects.all().delete()

    def test_create_post(self):
        data = {
            'content': 'new post'
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['content'], data['content'])
        self.assertIsNotNone(response.data['id'])
        self.assertIsNotNone(response.data['created_at'])
        self.assertIsNone(response.data['pics'])
        self.assertEqual(response.data['user']['username'], self.user.username)
        self.assertEqual(response.data['user']['id'], self.user.id)

        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.get().content, data['content'])

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_create_post_with_image(self):

        data = {
            'content': 'new post',
            'pics': get_temporary_image()
        }

        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['content'], data['content'])
        self.assertIsNotNone(response.data['id'])
        self.assertIsNotNone(response.data['created_at'])
        self.assertIsNotNone(response.data['pics'])
        self.assertEqual(response.data['user']['username'], self.user.username)
        self.assertEqual(response.data['user']['id'], self.user.id)

    def test_failure(self):
        response = self.client.post(self.url, format='json')
        self.assertEqual(response.status_code, 400)

    def test_create_post_with_no_content(self):

        data = {
            'pics': get_temporary_image()
        }

        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, 400)


class ViewCommentsTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user_john = User.objects.create_user(
            username='john', password='12345', email='john@gmail.com')
        self.user_bion = User.objects.create_user(
            username='bion', password='67890', email='bion@gmail.com')
        self.post = Post.objects.create(
            content="Test content", user=self.user_bion)

        self.comment_1 = Comment.objects.create(
            content="my first post", user=self.user_john, post=self.post)
        self.comment_2 = Comment.objects.create(
            content="then this is my first comment",
            user=self.user_bion,
            post=self.post)
        
    def teardown(self):
        User.objects.all().delete()



    def test_view_comments(self):
        # Define the URL for the endpoint
        url = f'/api/view-comments/{self.post.id}/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        comments_data = response.json()
        self.assertEqual(len(comments_data), 2)
        self.assertIn('id', comments_data[0])
        self.assertIn('content', comments_data[0])
        self.assertIn('user', comments_data[0])
        self.assertIn('username', comments_data[0]['user'])
        self.assertEqual(
            comments_data[0]['user']['username'],
            self.user_john.username)
        self.assertEqual(comments_data[0]['user']['id'], self.user_john.id)

        self.assertIn('id', comments_data[1])
        self.assertIn('content', comments_data[1])
        self.assertIn('user', comments_data[1])
        self.assertIn('username', comments_data[1]['user'])
        self.assertEqual(
            comments_data[1]['user']['username'],
            self.user_bion.username)
        self.assertEqual(comments_data[1]['user']['id'], self.user_bion.id)

    def test_with_wrong_id(self):
        false_id = 'd0fd92cd-65ba-41c8-ba4a-fa6d0dc07368'
        url = f'/api/view-comments/{false_id}/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_with_no_uuid_id(self):
        false_id = 'string_id'
        url = f'/api/view-comments/{false_id}/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 400)


class CreateCommentTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='john', password='password123', email='b@gmail.com')
        self.client.login(username='john', password='password123')
        self.post = Post.objects.create(user=self.user, content='Test post')
        self.url = reverse('create_comment', args=[self.post.id])

    def test_create_comment(self):
        data = {
            'content': 'new comment'
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['content'], data['content'])
        self.assertEqual(response.data['user']['username'], self.user.username)
        self.assertEqual(response.data['user']['id'], self.user.id)
        self.assertIn('id', response.data)

    def test_create_comment_invalid_data(self):
        data = {None}

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, 400)

    def test_create_comment_missing_post_id(self):
        # Test scenario where the post ID doesn't exist
        invalid_url = reverse('create_comment', args=['invalid-post-id'])

        data = {
            'content': 'new comment'
        }

        response = self.client.post(invalid_url, data, format='json')

        self.assertEqual(response.status_code, 400)


class LikesViewTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='john', password='password123', email='b@gmail.com')
        self.client.login(username='john', password='password123')
        self.post = Post.objects.create(user=self.user, content='Test post')
        # Assuming the URL name is 'like-post'
        self.url = reverse('toggele-like', args=[self.post.id])

    def test_like_post(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, self.post.likes.count())

    def test_unlike_post(self):
        # Like the post first
        like = Like.objects.create(post=self.post, user=self.user)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, self.post.likes.count())

    def test_unlike_when_no_like(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, self.post.likes.count())

    def test_wrong_string_id(self):
        self.url = reverse('toggele-like', args=['wrong id'])
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_wrong_nonexisting_id(self):
        self.url = reverse(
            'toggele-like',
            args=['9f7f4e93-535c-4859-8d88-fa388ab3db4a'])
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 404)


class ProfileViewTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='john2', password='12345', email='bion25@gmail.com')
        self.url = reverse('view_profile', kwargs={'user_id': self.user.id})

    def test_get_profile(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user_name'], 'john2')
        self.assertEqual(response.data['email'], 'bion25@gmail.com')
        self.assertIsNone(response.data['profile_pice'])
        self.assertIsNone(response.data['bio'])

    def test_with_wrong_id(self):
        self.url = reverse('view_profile', kwargs={'user_id': 4})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)


class ProfileViewTestUpdates(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='12345',
            email='testuser@example.com')
        self.url = reverse('edit_profile', kwargs={'user_id': self.user.id})

    def test_put_update_bio(self):
        updated_data = {'bio': 'Updated bio'}
        response = self.client.put(self.url, updated_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['bio'], updated_data['bio'])
        self.assertEqual(response.data['user_name'], self.user.username)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertIsNone(response.data['profile_pic'])

    def test_put_update_profile_pic(self):
        updated_data = {'profile_pic': get_temporary_image()}
        response = self.client.put(self.url, updated_data, format='multipart')
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data['profile_pic'])
        self.assertTrue(response.data['profile_pic'].endswith('jpg'))
        self.assertEqual(response.data['user_name'], self.user.username)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['bio'], None)

    def test_put_update_username_email(self):
        updated_data = {
            'username': 'updateduser',
            'email': 'updateduser@example.com'}
        response = self.client.put(self.url, updated_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user_name'], updated_data['username'])
        self.assertEqual(response.data['email'], updated_data['email'])
        self.assertIsNone(response.data['profile_pic'])
        self.assertEqual(response.data['bio'], None)

    def test_with_wrong_password(self):
        self.url = reverse('edit_profile', kwargs={'user_id': 44})
        updated_data = {
            'username': 'updateduser',
            'email': 'updateduser@example.com'}
        response = self.client.put(self.url, updated_data, format='json')
        self.assertEqual(response.status_code, 404)

    def test_with_no_data_passed(self):
        updated_data = {}
        response = self.client.put(self.url, updated_data, format='json')
        self.assertEqual(response.status_code, 200)

class GoogleLoginRedirectApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
    @patch('social_app.google_login_flow.GoogleRawLoginFlowService.get_authorization_url')
    def test_google_login_redirect(self, Mockget_authorization_url):
        
        Mockget_authorization_url.return_value = ('http://example.com/auth', 'test_state')

        # Create a request object
        response = self.client.get(reverse('google-oauth2-login-raw-redirect')) 

        # Assertions
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'http://example.com/auth')
        Mockget_authorization_url.assert_called_once()

class GoogleLoginApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_google_login_missing_with_error(self):
        response = self.client.get(reverse('google_auth2'), {
            'code': 'valid_code', 'state': 'valid_state', 'error': 12})
        self.assertEqual(response.status_code, 400)

    def test_google_login_missing_code(self):
        response = self.client.get(reverse('google_auth2'), {'state': 'valid_state'})
        self.assertEqual(response.status_code, 400)

    def test_google_login_missing_state(self):
        response = self.client.get(reverse('google_auth2'), {
            'code': 'valid_code'})
        self.assertEqual(response.status_code, 400)

    
    @patch('social_app.google_login_flow.GoogleRawLoginFlowService.get_tokens')
    @patch('social_app.views.generate_tokens_for_user')
    def test_google_login_success(self, mock_generate_tokens, mockGetTokens):
        
        googleacesstoken = MagicMock()
        mock_generate_tokens.return_value = {'access_token': '12312', 'refresh_token': 'qqqqq'}
        mockGetTokens.return_value = googleacesstoken
        googleacesstoken.decode_id_token.return_value = {'email': 'test@example.com', 'name': 'Test User', }

        response = self.client.get(reverse('google_auth2'), {'code': 'refresh_token', 'state': 'valid_state'})

        self.assertEqual(response.status_code, 200)
        mock_generate_tokens.assert_called_once()
        mockGetTokens.assert_called_with(code='refresh_token')
        self.assertEqual(response.data['user'], 'test@example.com')
        self.assertEqual(response.data['access_token'], 'access_token' )
        self.assertEqual(response.data['refresh_token'], 'refresh_token')