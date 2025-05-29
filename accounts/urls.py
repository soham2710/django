from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # API URLs
    path('api/register/', views.RegisterAPIView.as_view(), name='api_register'),
    path('api/login/', views.LoginAPIView.as_view(), name='api_login'),
    path('api/logout/', views.LogoutAPIView.as_view(), name='api_logout'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/profile/', views.ProfileAPIView.as_view(), name='api_profile'),
    path('api/profile/<str:username>/', views.UserProfileAPIView.as_view(), name='api_user_profile'),
    path('api/update/', views.UserUpdateAPIView.as_view(), name='api_user_update'),
    path('api/change-password/', views.ChangePasswordAPIView.as_view(), name='api_change_password'),
    
    # Template URLs
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
]