from rest_framework import serializers
from .models import Post, Comment, Like
from django.contrib.auth.models import User


class UserSerialiser(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'id']

class BaseSerialiser(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    created_at = serializers.DateTimeField(
        format="%B %d, %Y, %I:%M %p", read_only=True)
    updated_at = serializers.DateTimeField(
        format="%B %d, %Y, %I:%M %p", read_only=True)
    user = UserSerialiser(read_only=True)
    

class PostSerialiser(BaseSerialiser):
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Post
        fields = ['id', 'created_at', 'content',
                  'pics', 'user', 'likes_count', 'comments_count']
        ordering = ['id']
        
class CommentSerialiser(BaseSerialiser):
    class Meta:
        model = Comment
        fields = ['id', 'content', 'user']

