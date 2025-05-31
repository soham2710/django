from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('bio', 'location', 'birth_date', 'avatar', 'website', 'twitter', 'github', 'linkedin', 'phone', 'is_public')

# class ProfileInline(admin.TabularInline):
#     model = Profile
#     can_delete = False
#     verbose_name_plural = 'Profile'
#     fields = ('bio', 'location', 'birth_date', 'avatar', 'website', 'twitter', 'github', 'linkedin', 'phone', 'is_public')

@admin.register(User)
#admin.site.register(User,UserAdmin)
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_verified', 'is_staff', 'is_active', 'created_at')
    list_filter = ('is_staff', 'is_active', 'is_verified', 'created_at')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('User Info', {'fields': ('username', 'password','first_name', 'last_name', 'email')}),
        
        ('Permissions (Access Control)', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )

    add_fieldsets = ( # Creates new user in the admin panel
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'website', 'is_public', 'created_at', 'avatar_preview')
    list_filter = ('is_public', 'created_at', 'location')
    search_fields = ('user__username', 'user__email', 'bio', 'location')
    readonly_fields = ('created_at', 'updated_at', 'avatar_preview')
    
    fieldsets = (
        ('User Info', {'fields': ('user',)}),
        ('Profile Details', {'fields': ('bio', 'location', 'birth_date', 'phone')}),
        ('Avatar', {'fields': ('avatar', 'avatar_preview')}),
        ('Social Links', {'fields': ('website', 'twitter', 'github', 'linkedin')}),
        ('Settings', {'fields': ('is_public',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.avatar.url)
        return "No Avatar"
    avatar_preview.short_description = "Avatar Preview"