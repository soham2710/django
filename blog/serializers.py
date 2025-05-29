from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Category, Tag, Post, Comment, Like

User = get_user_model()

class CategorySerializer(serializers.ModelSerializer):
    posts_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('created_at',)

    def get_posts_count(self, obj):
        return obj.posts.filter(status='published').count()

class TagSerializer(serializers.ModelSerializer):
    posts_count = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('created_at',)

    def get_posts_count(self, obj):
        return obj.posts.filter(status='published').count()

class AuthorSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'full_name', 'avatar_url')

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def get_avatar_url(self, obj):
        if hasattr(obj, 'profile') and obj.profile.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile.avatar.url)
            return obj.profile.avatar.url
        return None

class CommentSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('author', 'created_at', 'updated_at')

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(
                obj.replies.filter(is_approved=True),
                many=True,
                context=self.context
            ).data
        return []

    def get_can_edit(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.author == request.user
        return False

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

class PostListSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    reading_time = serializers.ReadOnlyField()
    comments_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    featured_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id', 'title', 'slug', 'author', 'category', 'tags', 'excerpt',
            'featured_image_url', 'status', 'is_featured', 'views_count',
            'likes_count', 'reading_time', 'comments_count', 'is_liked',
            'published_at', 'created_at', 'updated_at'
        )

    def get_comments_count(self, obj):
        return obj.comments.filter(is_approved=True).count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_featured_image_url(self, obj):
        if obj.featured_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.featured_image.url)
            return obj.featured_image.url
        return None

class PostDetailSerializer(PostListSerializer):
    comments = serializers.SerializerMethodField()

    class Meta(PostListSerializer.Meta):
        fields = PostListSerializer.Meta.fields + ('content', 'meta_description', 'meta_keywords', 'comments')

    def get_comments(self, obj):
        comments = obj.comments.filter(parent=None, is_approved=True).order_by('created_at')
        return CommentSerializer(comments, many=True, context=self.context).data

class PostCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            'title', 'category', 'tags', 'content', 'excerpt',
            'featured_image', 'status', 'is_featured', 'meta_description', 'meta_keywords'
        )

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        tags = validated_data.pop('tags', [])
        post = Post.objects.create(**validated_data)
        post.tags.set(tags)
        return post

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if tags is not None:
            instance.tags.set(tags)
        
        return instance

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'
        read_only_fields = ('user', 'created_at')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)