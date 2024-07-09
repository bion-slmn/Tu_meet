from django.test import TestCase
from django.contrib.auth.models import User
from social_app.models import Profile
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


