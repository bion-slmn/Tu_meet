from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from social_app.models import Post, Comment, Like
from django.db.utils import IntegrityError
from django.db.transaction import TransactionManagementError
import uuid

class BaseModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.post = Post.objects.create(content="Sample post content", user=self.user)

    def test_base_model_fields(self):
        """
        Test that Base model fields are correctly set.
        """
        post1 = Post.objects.create(content="Sample post content", user=self.user)
        self.assertNotEqual(self.post.id, post1.id)
        self.assertGreater(self.post.updated_at, self.post.created_at)
        self.assertEqual(self.post.user, self.user)

    def test_post_content_field(self):
        """
        Test that the content field is correctly set.
        """
        self.assertEqual(self.post.content, "Sample post content")

    def test_post_image_field(self):
        """
        Test that the image field can accept an image file.
        """
        image_file = SimpleUploadedFile("sample.jpg", b"file_content", content_type="image/jpeg")
        post_with_image = Post.objects.create(content="Image post", user=self.user, pics=image_file)
        self.assertIsNotNone(post_with_image.pics.name)

    def test_post_validation(self):
        """
        Test that the model validates correctly.
        """
        # Test required fields
        with self.assertRaises(IntegrityError):
            Post.objects.create(content=None, user=self.user)
        with self.assertRaises(TransactionManagementError):
            Post.objects.create(content="Valid content", user=None)




class CommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.post = Post.objects.create(content="Sample post content", user=self.user)
        self.comment = Comment.objects.create(content="Great post!", post=self.post, user=self.user)

    def test_comment_fields(self):
        """
        Test that the comment fields are correctly set.
        """
        self.assertEqual(self.comment.content, "Great post!")
        self.assertEqual(self.comment.post, self.post)
        self.assertEqual(self.comment.user, self.user)

    def test_inherited_fields(self):
        """
        Test that the inherited fields from BaseModel are correctly set.
        """
        self.assertIsInstance(self.comment.id, uuid.UUID)
        self.assertEqual(self.comment.user, self.user)

    def test_foreign_key_relationship(self):
        """
        Test that the ForeignKey relationship to Post works correctly.
        """
        self.assertIn(self.comment, self.post.comments.all())

    def test_post_content_field(self):
        """
        Test that the post's content field is correctly set through the comment.
        """
        self.assertEqual(self.post.content, "Sample post content")


class LikeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.post = Post.objects.create(content="Sample post content", user=self.user)
        self.like = Like.objects.create(post=self.post, user=self.user)

    def test_like_fields(self):
        """
        Test that the like fields are correctly set.
        """
        self.assertEqual(self.like.post, self.post)
        self.assertEqual(self.like.user, self.user)

    def test_inherited_fields(self):
        """
        Test that the inherited fields from BaseModel are correctly set.
        """
        self.assertIsInstance(self.like.id, uuid.UUID)
        self.assertEqual(self.like.user, self.user)

    def test_foreign_key_relationship(self):
        """
        Test that the ForeignKey relationship to Post works correctly.
        """
        self.assertIn(self.like, self.post.likes.all())

    def test_post_content_field(self):
        """
        Test that the post's content field is correctly set through the like.
        """
        self.assertEqual(self.post.content, "Sample post content")
