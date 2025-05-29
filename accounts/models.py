from django.contrib.auth.models import AbstractUser # django's built-in user model includes fields like username, firstname, lastname and email
from django.db import models # includes field types and model classes
from PIL import Image # image processing library - pillow resize, crop, format the image, convert 

class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email' # used for authentication
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email

'''def __str__(self):
        return self.email
        
        defines how a USER object is represented as a string - in this case we have our email'''

# 1 user - 1 profile set info
# Cascade = if parent is deleted, then all child objects depending on the parent are also deleted
class Profile(models.Model): # this creates a profile model to store additional info
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    # MEDIA_URL = '/media/' - media\avatars\default.jpg
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.jpg')
    website = models.URLField(blank=True)
    twitter = models.CharField(max_length=100, blank=True)
    github = models.CharField(max_length=100, blank=True)
    linkedin = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile" 
    # how a profile is displayed using just the username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # overrides the save method and calls the parent save( to make changes to the database)
        
        if self.avatar:
            img = Image.open(self.avatar.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.avatar.path)