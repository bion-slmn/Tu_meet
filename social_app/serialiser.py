from rest_framework import serializers
from .models import Post, Comment, User, Notification


class UserSerialiser(serializers.ModelSerializer):
    """
    Serializes User model data to include only 'username' and 
    'id' fields.
    """

    class Meta:
        model = User
        fields = ['username', 'id']


class BaseSerialiser(serializers.ModelSerializer):
    """
    Base serializer for common fields like 
    'id', 'created_at', 'updated_at', and 'user'.
    """

    id = serializers.UUIDField(read_only=True)
    created_at = serializers.DateTimeField(
        format="%B %d, %Y, %I:%M %p", read_only=True)
    updated_at = serializers.DateTimeField(
        format="%B %d, %Y, %I:%M %p", read_only=True)
    user = UserSerialiser(read_only=True)


class PostSerialiser(BaseSerialiser):
    """
    Serializer for Post model data including 'id', 'created_at', 
    'content', 'pics', 'user', 'likes_count', 'comments_count'.
    """

    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'created_at', 'content',
                  'pics', 'user', 'likes_count', 'comments_count']
        ordering = ['id']



class CommentSerialiser(BaseSerialiser):
    """
    Serializer for Comment model data including 'id', 
    'content', 'user'.
    """

    class Meta:
        model = Comment
        fields = ['id', 'content', 'user']

class InputSerializer(serializers.Serializer):
        """
        Serializer for input data with optional fields 'code', '
        error', and 'state'.
        """

        code = serializers.CharField(required=False)
        error = serializers.CharField(required=False)
        state = serializers.CharField(required=False)


class NotificationSerialiser(serializers.Serializer):
     """
    Serializer for Notification model data including all fields.
    """

     class Meta:
          model = Notification
          fields = '__all__'
