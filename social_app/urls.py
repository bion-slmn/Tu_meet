from django.urls import path
from .views import (
    PostView, PostDetails,
    CommentView, LikesView,
    ProfileView
)


urlpatterns = [
    # profiles urls
    path(
        'view-profile/<str:user_id>',
        ProfileView.as_view(),
        name='view_profile'),
    path(
        'edit-profile/<str:user_id>',
        ProfileView.as_view(),
        name='edit_profile'),

    # posts urls
    path('view-posts/', PostView.as_view(), name='all_posts'),
    path(
        'view-post/<str:post_id>/',
        PostDetails.as_view(),
        name='view_a_post'),
    path('create-post/', PostDetails.as_view(), name='create_post'),

    # comments paths
    path(
        'create-comment/<str:post_id>/',
        CommentView.as_view(),
        name='create_comment'),
    path(
        'delete-comment/<str:comment_id>/',
        CommentView.as_view(),
        name='delete_comment'),
    path(
        'view-comments/<str:post_id>/',
        CommentView.as_view(),
        name='view_comments'),

    # toggle like and dislike
    path(
        'toggle-like/<str:post_id>/',
        LikesView.as_view(),
        name='toggele-like'),

]
