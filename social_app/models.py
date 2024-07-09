from django.db import models
import uuid
from django.contrib.auth.models import User


class BaseModel(models.Model):
    """
    A base model representing common fields for all models.
    """
    id = models.UUIDField(
        default=uuid.uuid4, editable=False, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        """
        An options class for defining metadata options for a model.
        """
        ordering = ['created_at']
        abstract = True


class Post(BaseModel):
    """
    A model representing a post with text content and optional images.
    """
    content = models.TextField()
    pics = models.ImageField(upload_to='images/', null=True, blank=True)

    def __str__(self) -> str:
        return self.content[:15]


class Comment(BaseModel):
    """
    A model representing a comment with text content.
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments')
    content = models.TextField()

    def __str__(self) -> str:
        return self.content[:15]


class Like(BaseModel):
    """
    A model representing a like on a post.
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes')


class Profile(models.Model):
    """
    Represents a user profile with a one-to-one relationship to a User.

    Returns:
        str: The username of the associated User.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(
        upload_to='profile_pics/', null=True, blank=True)
    bio = models.TextField(null=True)

    def __str__(self):
        return self.user.username
