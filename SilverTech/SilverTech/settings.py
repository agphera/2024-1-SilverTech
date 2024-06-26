"""
Django settings for SilverTech project.

Generated by 'django-admin startproject' using Django 5.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import pymysql
pymysql.install_as_MySQLdb()

from pathlib import Path
import os
import json


# API 키 작성된 메모장 주소
keys_file_path = os.path.join('../API', 'api_keys.txt')

# 파일에서 API 키를 로드하는 함수
with open(keys_file_path, 'r', encoding='utf-8') as file:
    keys = json.load(file)


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = keys['django-key']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'cogpicture.duckdns.org', 'localhost']

# Application definition

INSTALLED_APPS = [
    'corsheaders',
    'login_and_training',  # 이 줄을 추가하세요.
    'user_level',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'drf_yasg', # Swaager
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',#1번째줄 필수
    'corsheaders.middleware.CorsMiddleware',#2번째줄
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',#3번째줄
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'SilverTech.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / '../Frontend_UI'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'SilverTech.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'oss',
        'USER': 'root',
        'PASSWORD': keys['mysql_pw'],
        'HOST': '35.194.147.127',
        'PORT': '3306',
        
    }
}



# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


#모든 도메인에서의 요청을 허용하려면 CORS_ALLOW_ALL_ORIGINS 설정을 True
CORS_ALLOW_ALL_ORIGINS = True



import os

# Django 프로젝트의 기본 디렉토리 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# MEDIA_ROOT 설정을 상대 경로로 지정, 저장 경로를 정해드립니다. 
MEDIA_ROOT = os.path.join(BASE_DIR, 'Media')

# MEDIA_URL 설정
MEDIA_URL = '/Media/'


# 다른 앱 사이에서 세션 공유
# SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies' # 브라우저 쿠키에 세션 저장
SESSION_COOKIE_AGE = 10800  # 세션 쿠키의 유효기간 (3시간)

## 여기 아래서부턴 서버 업로드용
# SESSION_COOKIE_DOMAIN = '.cogpicture.duckdns.org'  # '.yourdomain.com'으로 변경
# SESSION_COOKIE_SECURE = True  # HTTPS 사용 시 True로 설정
# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_NAME = 'sessionid'  # 세션 쿠키의 이름
