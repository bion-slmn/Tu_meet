from django.http import HttpRequest
from rest_framework.views import APIView
from rest_framework.response import Response
from .decorator import class_exception_handler
from .models import Post, Comment, Like
from rest_framework.generics import ListAPIView
from .serialiser import (
    PostSerialiser, CommentSerialiser)
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.db.models import Count
from django.contrib.auth.models import User


class PostView(ListAPIView):
    """
    A view class for listing posts using a specific queryset and serializer.
    """
    queryset = Post.objects.annotate(
        likes_count=Count('likes'), comments_count=Count('comments')).all()
    serializer_class = PostSerialiser

@class_exception_handler
class PostDetails(APIView):
    def get(self, request: HttpRequest, post_id: str) -> Response:
        """
        Handles GET requests to retrieve a specific post by 
        its ID and return its serialized data.


        Args:
            request: The HTTP request object.
            post_id: The ID of the post to retrieve.

        Returns:
            Response: The serialized data of the retrieved post.
        """ 

        post = get_object_or_404(
            Post.objects.annotate(
                likes_count=Count('likes'), 
                comments_count=Count('comments')),id=post_id)
        
        post_serialised = PostSerialiser(post).data
        return Response(post_serialised)
    
    def post(self, request: HttpRequest):
        """
        Handles POST requests to create a new post
          with user, content, and optional images.

        Args:
            request: The HTTP request object containing user, content, and pics data.

        Returns:
            Response: The serialized data of the newly created post.
        """ 

        data = {
        'content': request.data.get('content'),
        'pics': request.data.get('pics')
        }

        serializer = PostSerialiser(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@class_exception_handler
class CommentView(APIView):
    def post(self, request: HttpRequest, post_id: str) -> Response:
        """
        Handles POST requests to create a new comment on a specific post.

        Args:
            request: The HTTP request object containing the comment content.
            post_id: The ID of the post to comment on.

        Returns:
            Response: The serialized data of the newly created comment or error response.
        """ 

        post = get_object_or_404(Post, id=post_id)

        serialiser = CommentSerialiser(data={'content':request.data.get('content')})
        if serialiser.is_valid():
            serialiser.save(post=post, user=request.user)
            return Response(serialiser.data, status=status.HTTP_201_CREATED)
        return Response(serialiser.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request: HttpRequest, comment_id: str) -> Response:
        """
        Handles DELETE requests to delete a specific comment by its ID.

        Args:
            request: The HTTP request object.
            comment_id: The ID of the comment to delete.

        Returns:
            Response: A success message indicating the comment was deleted.
        """ 

        comment = get_object_or_404(Comment, id=comment_id)
        comment.delete()
        return Response('Successfully deleted')
    


class ViewComments(ListAPIView):
    """
    A view class for listing comments for a specific post.
    """
    
    def get_queryset(self):
        """
        Override this method to filter comments by post_id.
        """
        post_id = self.kwargs['post_id']
        return Comment.objects.filter(post_id=post_id)

    serializer_class = CommentSerialiser

