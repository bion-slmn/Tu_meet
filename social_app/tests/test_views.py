from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from social_app.models import Post, Like, Comment
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

class PostViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='12345')
        image_file = SimpleUploadedFile("sample.jpg", b"file_content", content_type="image/jpeg")
        self.post1 = Post.objects.create(content="Sample post content", user=self.user)
        self.post2 = Post.objects.create(content="Another sample post", user=self.user, pics=image_file)
        self.like = Like.objects.create(post=self.post1, user=self.user)
        self.comment = Comment.objects.create(content="Great post!", post=self.post1, user=self.user)
        self.response = self.client.get(reverse('all_posts'))
        
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
        self.user = User.objects.create_user(username='testuser', password='testpass')
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

    