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
    

class PostSerialiser(BaseSerialiser):
    user = UserSerialiser(read_only=True)
    class Meta:
        model = Post
        fields = ['id', 'created_at', 'updated_at', 'user', 'content', 'pics']