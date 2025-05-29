from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Profile
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    ProfileSerializer, UserUpdateSerializer, ChangePasswordSerializer
)

# API Views
class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user, context={'request': request}).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user, context={'request': request}).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

class LogoutAPIView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

class ProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile

class UserProfileAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'

class UserUpdateAPIView(generics.UpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class ChangePasswordAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)

# Template Views
def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match')
            return render(request, 'accounts/signup.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'accounts/signup.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'accounts/signup.html')
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password
            )
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('blog_list')
        except Exception as e:
            messages.error(request, 'Error creating account')
            return render(request, 'accounts/signup.html')
    
    return render(request, 'accounts/signup.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                login(request, user)
                messages.success(request, 'Login successful!')
                return redirect('blog_list')
            else:
                messages.error(request, 'Invalid credentials')
        except User.DoesNotExist:
            messages.error(request, 'Invalid credentials')
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('login')

@login_required
def profile_view(request):
    if request.method == 'POST':
        # Update profile
        profile = request.user.profile
        profile.bio = request.POST.get('bio', '')
        profile.location = request.POST.get('location', '')
        profile.website = request.POST.get('website', '')
        profile.twitter = request.POST.get('twitter', '')
        profile.github = request.POST.get('github', '')
        profile.linkedin = request.POST.get('linkedin', '')
        profile.phone = request.POST.get('phone', '')
        
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    return render(request, 'accounts/profile.html', {'user': request.user})