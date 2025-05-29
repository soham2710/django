from django.urls import path
from . import views

urlpatterns = [
    # API URLs
    path('api/posts/', views.PostListAPIView.as_view(), name='api_post_list'),
    path('api/posts/<slug:slug>/', views.PostDetailAPIView.as_view(), name='api_post_detail'),
    path('api/posts/create/', views.PostCreateAPIView.as_view(), name='api_post_create'),
    path('api/posts/<slug:slug>/update/', views.PostUpdateAPIView.as_view(), name='api_post_update'),
    path('api/posts/<slug:slug>/delete/', views.PostDeleteAPIView.as_view(), name='api_post_delete'),
    path('api/categories/', views.CategoryListAPIView.as_view(), name='api_category_list'),
    path('api/tags/', views.TagListAPIView.as_view(), name='api_tag_list'),
    path('api/comments/create/', views.CommentCreateAPIView.as_view(), name='api_comment_create'),
    path('api/comments/<int:pk>/update/', views.CommentUpdateAPIView.as_view(), name='api_comment_update'),
    path('api/comments/<int:pk>/delete/', views.CommentDeleteAPIView.as_view(), name='api_comment_delete'),
    path('api/posts/<uuid:post_id>/like/', views.LikeToggleAPIView.as_view(), name='api_like_toggle'),
    
    # Template URLs
    path('', views.blog_list, name='blog_list'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('create/', views.create_post, name='create_post'),
    path('like/<uuid:post_id>/', views.toggle_like, name='toggle_like'),
]