import os
from pathlib import Path
from datetime import timedelta
from decouple import config
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent # defining our root directory

SECRET_KEY = config('SECRET_KEY', default='django-insecure-c929e#&@@($1_x&g-_jg@&k7y!!gko=gpq8#q9!4_ngu!vo*-)')
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'accounts',
    'blog',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'blog_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates', # default template engine
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True, # allowing django to use app - specific folders
        'OPTIONS': { # sending data to templates
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'blog_project.wsgi.application'

# Database
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='postgresql://postgres:password@localhost:5432/blog_db'),
        conn_max_age=600
    )
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': config('DB_NAME', default='blog_db'),
#         'USER': config('DB_USER', default='postgres'),
#         'PASSWORD': config('DB_PASSWORD', default='password'),
#         'HOST': config('DB_HOST', default='localhost'),
#         'PORT': config('DB_PORT', default='5432'),
#     }
# }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static', # django will look for static files in this folder
]
STATIC_ROOT = BASE_DIR / 'staticfiles' #django will copy the files for production

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField' # Default auto incrementing primary key 

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60), # access toens expire after 60 mins
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1), # refresh tokens expire after 1 day/24 hours
    'ROTATE_REFRESH_TOKENS': True, # refresh tokens are rotated on each use i.e. generating new tokens
    'BLACKLIST_AFTER_ROTATION': True, # no usage of old tokens ever
    'UPDATE_LAST_LOGIN': False, # do not update last login time on token refresh
    'ALGORITHM': 'HS256',  # SHA256 algorithm for signing tokens
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    'AUTH_HEADER_TYPES': ('Bearer',), # type of authentication header
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION', # Standard http for authentication
    'USER_ID_FIELD': 'id', # field in the user model that stores the user id
    'USER_ID_CLAIM': 'user_id', # stores user id as token
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule', # default authentication by django
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',), 
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# CORS Configuration - Cross origin resource sharing settings 
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000", # react/node apps
    "http://127.0.0.1:3000",
    "http://localhost:8000", # django apps
    "http://127.0.0.1:8000",
]

# Login/Logout URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'