from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import Category, Tag, Post, Comment, Like, PostView

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'posts_count', 'color_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)

    def posts_count(self, obj):
        return obj.posts.count()
    posts_count.short_description = 'Posts Count'

    def color_preview(self, obj):
        return format_html(
            '<span style="background-color:{}; padding: 5px 10px; color: white; border-radius: 3px;">{}</span>',
            obj.color, obj.color
        )
    color_preview.short_description = 'Color'

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            posts_count=Count('posts')
        )

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'posts_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)

    def posts_count(self, obj):
        return obj.posts.count()
    posts_count.short_description = 'Posts Count'

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('author', 'created_at')
    fields = ('author', 'content', 'is_approved', 'created_at')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'is_featured', 'views_count', 'likes_count', 'created_at', 'image_preview')
    list_filter = ('status', 'is_featured', 'category', 'created_at', 'author')
    search_fields = ('title', 'content', 'author__username', 'author__email')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('id', 'views_count', 'likes_count', 'created_at', 'updated_at', 'reading_time', 'image_preview')
    filter_horizontal = ('tags',)
    inlines = [CommentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'category', 'tags')
        }),
        ('Content', {
            'fields': ('content', 'excerpt', 'featured_image', 'image_preview')
        }),
        ('Status & Settings', {
            'fields': ('status', 'is_featured', 'published_at')
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('views_count', 'likes_count', 'reading_time'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        if obj.featured_image:
            return format_html('<img src="{}" width="100" height="60" style="object-fit: cover;" />', obj.featured_image.url)
        return "No Image"
    image_preview.short_description = "Image Preview"

    def reading_time(self, obj):
        return f"{obj.reading_time} min read"
    reading_time.short_description = "Reading Time"

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'content_preview', 'is_approved', 'is_reply', 'created_at')
    list_filter = ('is_approved', 'created_at', 'post__category')
    search_fields = ('content', 'author__username', 'post__title')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('post', 'author', 'parent')

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'

    def is_reply(self, obj):
        return obj.is_reply
    is_reply.boolean = True
    is_reply.short_description = 'Is Reply'

    actions = ['approve_comments', 'unapprove_comments']

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    approve_comments.short_description = "Approve selected comments"

    def unapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)
    unapprove_comments.short_description = "Unapprove selected comments"

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    list_filter = ('created_at', 'post__category')
    search_fields = ('user__username', 'post__title')
    readonly_fields = ('created_at',)
    raw_id_fields = ('user', 'post')

@admin.register(PostView)
class PostViewAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'ip_address', 'created_at')
    list_filter = ('created_at', 'post__category')
    search_fields = ('post__title', 'user__username', 'ip_address')
    readonly_fields = ('created_at',)
    raw_id_fields = ('post', 'user')

# Customize admin site header
admin.site.site_header = "Blog Administration"
admin.site.site_title = "Blog Admin"
admin.site.index_title = "Welcome to Blog Administration"