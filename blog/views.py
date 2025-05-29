from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Post, Category, Tag, Comment, Like, PostView
from .serializers import (
    PostListSerializer, PostDetailSerializer, PostCreateUpdateSerializer,
    CategorySerializer, TagSerializer, CommentSerializer, LikeSerializer
)

# API Views
class PostListAPIView(generics.ListAPIView):
    serializer_class = PostListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Post.objects.filter(status='published').select_related('author', 'category').prefetch_related('tags', 'likes')
        
        # Search functionality
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(content__icontains=search) | 
                Q(excerpt__icontains=search)
            )
        
        # Category filter
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Tag filter
        tag = self.request.query_params.get('tag')
        if tag:
            queryset = queryset.filter(tags__slug=tag)
        
        # Author filter
        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author__username=author)
        
        # Featured posts
        featured = self.request.query_params.get('featured')
        if featured and featured.lower() in ['true', '1']:
            queryset = queryset.filter(is_featured=True)
        
        # Ordering
        ordering = self.request.query_params.get('ordering', '-created_at')
        if ordering in ['created_at', '-created_at', 'title', '-title', 'views_count', '-views_count', 'likes_count', '-likes_count']:
            queryset = queryset.order_by(ordering)
        
        return queryset

class PostDetailAPIView(generics.RetrieveAPIView):
    queryset = Post.objects.filter(status='published')
    serializer_class = PostDetailSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Track post view
        ip_address = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        view_obj, created = PostView.objects.get_or_create(
            post=instance,
            user=request.user if request.user.is_authenticated else None,
            ip_address=ip_address,
            defaults={'user_agent': user_agent}
        )
        
        if created:
            Post.objects.filter(pk=instance.pk).update(views_count=models.F('views_count') + 1)
            instance.refresh_from_db()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class PostCreateAPIView(generics.CreateAPIView):
    serializer_class = PostCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

class PostUpdateAPIView(generics.UpdateAPIView):
    serializer_class = PostCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

class PostDeleteAPIView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

class TagListAPIView(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]

class CommentCreateAPIView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

class CommentUpdateAPIView(generics.UpdateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(author=self.request.user)

class CommentDeleteAPIView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(author=self.request.user)

class LikeToggleAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
            like, created = Like.objects.get_or_create(user=request.user, post=post)
            
            if not created:
                like.delete()
                Post.objects.filter(pk=post.pk).update(likes_count=models.F('likes_count') - 1)
                return Response({'liked': False, 'likes_count': post.likes_count - 1})
            else:
                Post.objects.filter(pk=post.pk).update(likes_count=models.F('likes_count') + 1)
                return Response({'liked': True, 'likes_count': post.likes_count + 1})
        
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

# Template Views
def blog_list(request):
    posts = Post.objects.filter(status='published').select_related('author', 'category').prefetch_related('tags')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query) | 
            Q(excerpt__icontains=search_query)
        )
    
    # Category filter
    category_slug = request.GET.get('category')
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    
    # Tag filter
    tag_slug = request.GET.get('tag')
    if tag_slug:
        posts = posts.filter(tags__slug=tag_slug)
    
    # Pagination
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories and tags for filters
    categories = Category.objects.all()
    tags = Tag.objects.all()
    
    context = {
        'posts': page_obj,
        'categories': categories,
        'tags': tags,
        'search_query': search_query,
        'selected_category': category_slug,
        'selected_tag': tag_slug,
    }
    
    return render(request, 'blog/blog_list.html', context)

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    
    # Track post view
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    view_obj, created = PostView.objects.get_or_create(
        post=post,
        user=request.user if request.user.is_authenticated else None,
        ip_address=ip_address,
        defaults={'user_agent': user_agent}
    )
    
    if created:
        post.views_count += 1
        post.save()
    
    # Get comments
    comments = post.comments.filter(parent=None, is_approved=True).order_by('created_at')
    
    # Check if user liked the post
    is_liked = False
    if request.user.is_authenticated:
        is_liked = post.likes.filter(user=request.user).exists()
    
    # Handle comment submission
    if request.method == 'POST' and request.user.is_authenticated:
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        
        if content:
            parent = None
            if parent_id:
                try:
                    parent = Comment.objects.get(id=parent_id, post=post)
                except Comment.DoesNotExist:
                    pass
            
            Comment.objects.create(
                post=post,
                author=request.user,
                parent=parent,
                content=content
            )
            
            messages.success(request, 'Comment added successfully!')
            return redirect('post_detail', slug=slug)
    
    context = {
        'post': post,
        'comments': comments,
        'is_liked': is_liked,
    }
    
    return render(request, 'blog/post_detail.html', context)

@login_required
def create_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        excerpt = request.POST.get('excerpt')
        category_id = request.POST.get('category')
        status = request.POST.get('status', 'draft')
        
        if title and content:
            post = Post.objects.create(
                title=title,
                content=content,
                excerpt=excerpt,
                author=request.user,
                status=status
            )
            
            if category_id:
                try:
                    category = Category.objects.get(id=category_id)
                    post.category = category
                    post.save()
                except Category.DoesNotExist:
                    pass
            
            # Handle tags
            tags_input = request.POST.get('tags', '')
            if tags_input:
                tag_names = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
                for tag_name in tag_names:
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    post.tags.add(tag)
            
            # Handle featured image
            if 'featured_image' in request.FILES:
                post.featured_image = request.FILES['featured_image']
                post.save()
            
            messages.success(request, 'Post created successfully!')
            return redirect('post_detail', slug=post.slug)
    
    categories = Category.objects.all()
    return render(request, 'blog/create_post.html', {'categories': categories})

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_like(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        
        if not created:
            like.delete()
            post.likes_count -= 1
            post.save()
            return JsonResponse({'liked': False, 'likes_count': post.likes_count})
        else:
            post.likes_count += 1
            post.save()
            return JsonResponse({'liked': True, 'likes_count': post.likes_count})
    
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip