from django.http import HttpRequest
from rest_framework.views import APIView
from rest_framework.response import Response
from .decorator import class_exception_handler
from .models import Post, Comment, Like, User
from rest_framework.generics import ListAPIView
from .serialiser import (
    PostSerialiser, CommentSerialiser, InputSerializer)
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.db.models import Count
from .google_login_flow import GoogleRawLoginFlowService, generate_tokens_for_user
from rest_framework import  status
import os
from django.shortcuts import redirect



class PostView(ListAPIView):
    """
    A view class for listing posts using a specific queryset and serializer.
    """
    queryset = Post.objects.annotate(
        likes_count=Count('likes'), comments_count=Count(
            'comments')).order_by('created_at').all()
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
                comments_count=Count('comments')), id=post_id)

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
            'pics': request.FILES.get('pics')
        }

        serializer = PostSerialiser(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@class_exception_handler
class CommentView(APIView):

    def get(self, request: HttpRequest, post_id):
        """
        Retrieves comments related to a specific post.

        Args:
            request: HttpRequest object representing the request.
            post_id: ID of the post to retrieve comments for.

        Returns:
            CommentSerialiser: A serialized representation of the
            comments related to the specified post.
        """
        comments = Comment.objects.filter(post_id=post_id)
        return Response(CommentSerialiser(comments, many=True).data)

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

        serialiser = CommentSerialiser(
            data={'content': request.data.get('content')})
        if serialiser.is_valid():
            serialiser.save(post=post, user=request.user)
            return Response(serialiser.data, status=status.HTTP_201_CREATED)
        return Response('here', status=status.HTTP_400_BAD_REQUEST)

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


@class_exception_handler
class LikesView(APIView):
    def post(self, request: HttpRequest, post_id) -> Response:
        """
        Handles liking or unliking a post.

        Args:
            request: HttpRequest object representing the request.
            post_id: ID of the post to like or unlike.

        Returns:
            Response: The number of likes the post currently has
            after the like/unlike operation.
        """
        post = get_object_or_404(Post, id=post_id)
        like, created = Like.objects.get_or_create(
            post=post, user=request.user)
        if not created:
            like.delete()
        return Response(post.likes.count())


@class_exception_handler
class ProfileView(APIView):
    def get(self, request: HttpRequest, user_id: str) -> Response:
        """
        Retrieves user information including username,
        email, profile picture, and bio.

        Args:
            request: The HTTP request object.
            user_id: The ID of the user to retrieve information for.

        Returns:
            Response: A response containing the user's
            username, email, profile picture, and bio.
        """

        user = get_object_or_404(
            User.objects.select_related('profile'), id=user_id)
        return Response(
            {'user_name': user.username,
             'email': user.email,
             'profile_pice': (
                 user.profile.profile_pic.url if
                 user.profile.profile_pic else None),
             'bio': user.profile.bio
             }
        )

    def put(self, request: HttpRequest, user_id: str) -> Response:
        """
        Updates the bio and profile picture of a user's profile.

        Args:
            request: The HTTP request object.
            user_id: The ID of the user whose profile is being updated.

        Returns:
            Response: A response containing the updated user
            information including username, email, profile picture, and bio.
        """

        user = get_object_or_404(
            User.objects.select_related('profile'), id=user_id)
        profile = user.profile
        profile.bio = request.data.get('bio', profile.bio)
        profile.profile_pic = request.FILES.get(
            'profile_pic', profile.profile_pic)
        user.username = request.data.get('username', user.username)
        user.email = request.data.get('email', user.email)
        profile.save()
        user.save()

        return Response(
            {
                'user_name': user.username,
                'email': user.email,
                'profile_pic': (
                    profile.profile_pic.url if profile.profile_pic else None),
                'bio': profile.bio
            },
            status=status.HTTP_200_OK
        )
    
class PublicApi(APIView):
    """
    An API view that allows public access without
    requiring authentication or permissions.
    """
    authentication_classes = ()
    permission_classes = ()


class GoogleLoginRedirectApi(PublicApi):
    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to initiate the Google OAuth2 login flow.

        Args:
            request (HttpRequest): The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            HttpResponseRedirect: Redirects to the Google OAuth2 
            authorization URL.
        """
        google_login_flow = GoogleRawLoginFlowService()

        authorization_url, state = google_login_flow.get_authorization_url()

        request.session["google_oauth2_state"] = state
        return redirect(authorization_url)
    
class GoogleLoginApi(PublicApi):

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to process Google OAuth2 login callback.

        Args:
            request (HttpRequest): The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: JSON response containing user information after successful login.
        """
        input_serializer = InputSerializer(data=request.GET)
        input_serializer.is_valid(raise_exception=True)

        validated_data = input_serializer.validated_data

        code = validated_data.get("code")
        error = validated_data.get("error")
        state = validated_data.get("state")

        if error is not None:
            return Response(
                {"error": error},
                status=status.HTTP_400_BAD_REQUEST
            )

        if code is None or state is None:
            return Response(
                {"error": "Code and state are required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )


        google_login_flow = GoogleRawLoginFlowService()
        google_tokens = google_login_flow.get_tokens(code=code)
        
        id_token_decoded = google_tokens.decode_id_token(
            client_id=os.getenv('GOOGLE_OAUTH2_CLIENT_ID'))
        #user_info = google_login_flow.get_user_info(google_tokens=google_tokens)
        
        user_email = id_token_decoded.get("email")
        user_name = id_token_decoded.get("name")
        user, _ = User.objects.get_or_create(email=user_email, username=user_name)
        
        try:
            user = User.objects.get(email=user_email)
            
        except User.DoesNotExist:
            username = user_email.split('@')[0]
            first_name = id_token_decoded.get('given_name', '')
            last_name = id_token_decoded.get('family_name', '')

            user = User.objects.create(
                username=username,
                email=user_email,
                first_name=first_name,
                last_name=last_name,
                registration_method='google',
                phone_no=None,
                referral=None
            )
        finally:
            access_token, refresh_token = generate_tokens_for_user(user)
            response_data = {
                'user': user_email,
                'access_token': str(access_token),
                'refresh_token': str(refresh_token)
            }
            return Response(response_data)