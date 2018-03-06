"""
Django settings for django_wu project.

Generated by 'django-admin startproject' using Django 1.10.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '8*md2t)o**67@*yhc(d=f@j95kl(dnf^rmm4s00$-mh_vurb2b'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '192.168.1.11', '192.168.1.12', '10.*', '10.74.26.114']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'app_temple',
    'app_docker',
    'app_node',
    'jenkins_manager'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'my_sites.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'my_sites.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATIC_URL = '/static/'

# log config

# ADMINS = (
#     # ('Your Name', 'your_email@example.com'),
# )
#
# MANAGERS = ADMINS

# DEFAULT_FROM_EMAIL = 'noreply@example.com'
# SERVER_EMAIL = 'admin@example.com'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {  # 日志格式
        'verbose': {  # 详细格式
             'format': '[%(filename)s:%(lineno)s %(funcName)1s()] %(levelname)s %(asctime)s %(message)s'
        },
        'simple': {  # 简单格式
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {  # 日志过滤器
        # 'special': {  # 特殊过滤器，替换foo成bar，可以自己配置
        #     '()': 'project.logging.SpecialFilter',
        #     'foo': 'bar',
        # },
        'require_debug_true': {  # 是否支持DEBUG级别日志过滤
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {  # 日志handlers
        'file': {  # 文件handler
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': './controller.log'
        },
        'console': {  # 控制器handler，INFO级别以上的日志都要Simple格式输出到控制台
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },

        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            # 仅当 DEBUG = False 时才发送邮件
            # 'filters': ['require_debug_false', 'special'],
            'class': 'django.utils.log.AdminEmailHandler',

        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        # 对于不在 ALLOWED_HOSTS 中的请求不发送报错邮件
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
        'jenkins_manager': {
            'handlers': ['console', 'mail_admins', 'file'],
            'level': 'DEBUG',
            # 'filters': ['special']
        }

    }
}

LOGIN_URL = '/login/'
# LOGIN_URL = '/login/'
# LOGIN_REDIRECT_URL = '/user/accounts/'
