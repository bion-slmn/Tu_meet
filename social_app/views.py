from django.http import HttpRequest
from rest_framework.views import APIView
from rest_framework.response import Response
from .decorator import class_exception_handler
from .models import Post, Comment, Like
from rest_framework.generics import ListAPIView
from .serialiser import PostSerialiser
from django.shortcuts import get_object_or_404
from rest_framework import status


class PostView(ListAPIView):
    """
    A view class for listing posts using a specific queryset and serializer.
    """
    queryset = Post.objects.all()
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

        post = get_object_or_404(Post, id=post_id)
        serialiser = PostSerialiser(post)
        return Response(serialiser.data)
    
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

        serializer = PostSerialiser(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)  # Save the instance via the serializer
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

