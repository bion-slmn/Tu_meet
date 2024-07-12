from django.test import TestCase
from social_app.models import User
from social_app.models import Profile, Notification, Like, Comment, Post
from django.db.utils import IntegrityError


class ProfileSignalTest(TestCase):
    def test_profile_created(self):
        user = User.objects.create_user(username='testuser', password='12345')
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_profile_takes_only_one_profie(self):
        user = User.objects.create_user(username='testuser1', password='12345')
        with self.assertRaises(IntegrityError):
            Profile.objects.create(user=user)

    def test_bio_and_pic_are_empty(self):
        user = User.objects.create_user(username='testuser2', password='12345')
        self.assertEqual(user.profile.bio, None)
        self.assertEqual(user.profile.profile_pic, None)
        self.assertEqual(user.profile.user, user)


class NotificationTests(TestCase):

    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(email='b@gmail.com',username='user1', password='testpassword1')
        self.user2 = User.objects.create_user(username='user2', password='testpassword2', email='bd@gmail.com')
        self.post = Post.objects.create(user=self.user1, content='Test post content')
    
    def teardown(self):
        Notification.objects.all().delete()

    def test_comment_notification_creation(self):
        comment = Comment.objects.create(post=self.post, user=self.user2, content='Test comment')
        notification = Notification.objects.all()
        self.assertEqual(len(notification), 1)
        self.assertEqual(notification[0].user, self.user2)
        self.assertEqual(notification[0].message, 'user2 commented on your post')

    def test_like_notification_creation(self):
        like = Like.objects.create(post=self.post, user=self.user2)
        notification = Notification.objects.all()
        self.assertEqual(len(notification), 1)
        self.assertEqual(notification[0].user, self.user2)
        self.assertEqual(notification[0].message, 'user2 liked your post')

    def test_no_self_notification_for_comment(self):
        # Simulate self-comment creation
        comment = Comment.objects.create(post=self.post, user=self.user1, content='Self comment')
        notifications = Notification.objects.all()
        self.assertEqual(notifications.count(), 0)

    def test_no_self_notification_for_like(self):
        like = Like.objects.create(post=self.post, user=self.user1)
        notifications = Notification.objects.all()
        self.assertEqual(notifications.count(), 0)

