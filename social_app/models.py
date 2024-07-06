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
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()

    def __str__(self) -> str:
        return self.content[:15]


class Like(BaseModel):
    """
    A model representing a like on a post.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')