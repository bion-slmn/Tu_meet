from django.urls import path
from .views import (
    PostView, PostDetails,
    CommentView
)


urlpatterns = [
    path('view-posts/', PostView.as_view(), name='all_posts'),
    path('view-post/<str:post_id>', PostDetails.as_view(), name='view_a_post'),
    path('create-post/', PostDetails.as_view(), name='create_post'),

    # comments paths
    path('create-comment/<str:post_id>', CommentView.as_view(), name='create_comment'),
]