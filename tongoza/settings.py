"""
Django settings for tongoza project.

Generated by 'django-admin startproject' using Django 3.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import os
from pathlib import Path
import environ
import django_heroku

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    "https://20d7fecf5d1f461e88f0b8df83695c64@o974969.ingest.sentry.io/5930816",

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)
env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
# reading .env file
# print('env:', env)
environ.Env.read_env()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = env('DEBUG')

print("debug", DEBUG)

ALLOWED_HOSTS = ['*']

CANON_URL_HOST = 'www.tongoza.com'
CANON_URLS_TO_REWRITE = ['tongoza.com', 'tongoza.herokuapp.com']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.flatpages',

    'asymmetric_jwt_auth',
    'certbot_django.server',

    # installed
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'crispy_forms',
    'ckeditor',
    "corsheaders",
    'debug_toolbar',
    'phonenumber_field',
    'storages',
    'django_db_logger',
    'mptt',

    # My apps
    'friend',
    'tongozahome',
    'users',
    'utils',
    'marketing',

]

CRISPY_TEMPLATE_PACK = 'bootstrap4'

LOGIN_REDIRECT_URL = 'tongozahome:home'

SITE_ID = 1

MIDDLEWARE = [

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'marketing.urlcanon.URLCanonicalizationMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'asymmetric_jwt_auth.middleware.JWTAuthMiddleware',


]

# CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = 'tongoza.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        # 'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'utils.context_processors.tongoza',
            ],
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ]

        },
    },
]
AUTHENTICATION_BACKENDS = [

    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',

]

WSGI_APPLICATION = 'tongoza.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

if not DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'tongozana',
            'USER': os.environ.get('USER'),
            'PASSWORD': os.environ.get('PASSWORD'),
            'HOST': 'localhost',
        }
    }

    import dj_database_url

    db_from_env = dj_database_url.config(conn_max_age=600)
    DATABASES['default'].update(db_from_env)


# DISABLE_SERVER_SIDE_CURSORS = True  # required when using pgbouncer's pool_mode=transaction

SITE_NAME = 'Ongoza'
META_KEYWORDS = 'Social Media, Therapy site, Buddy System, Moments Sharing'
META_DESCRIPTION = 'Ongoza is a leadership social platform where users can share moments. We call it ' \
                   'a Buddy system where you and I can become Buddies and Accountability Partners.'


CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

# stripe settings


# servers = os.environ['MEMCACHIER_SERVERS']
# username = os.environ['MEMCACHIER_USERNAME']
# password = os.environ['MEMCACHIER_PASSWORD']
#
# CACHES = {
#     'default': {
#         # Use django-bmemcached
#         'BACKEND': 'django_bmemcached.memcached.BMemcached',
#
#         # TIMEOUT is not the connection timeout! It's the default expiration
#         # timeout that should be applied to keys! Setting it to `None`
#         # disables expiration.
#         # 'TIMEOUT': None,
#         'TIMEOUT': 600,
#
#         'LOCATION': servers,
#
#         'OPTIONS': {
#             'username': username,
#             'password': password,
#         }
#     }
# }

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
    },
    'handlers': {
        'db_log': {
            'level': 'DEBUG',
            'class': 'django_db_logger.db_log_handler.DatabaseLogHandler'
        },
    },
    'loggers': {
        'db': {
            'handlers': ['db_log'],
            'level': 'DEBUG'
        }
    }
}
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
    },

    'Special': {
        'toolbar': 'Special',
        'toolbar_Special': [
            ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Print', 'SpellChecker', 'Scayt'],
            ['Undo', 'Redo', '-', 'Find', 'Replace', '-', 'SelectAll', 'RemoveFormat'],
            '/',
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Smiley', 'SpecialChar'],
        ]

    }

}

AUTH_USER_MODEL = 'users.User'

ACCOUNT_EMAIL_REQUIRED = True
# ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = None

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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

# debug toolbar requirement
INTERNAL_IPS = [
    '127.0.0.1',
]

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATICFILES_STORAGE = 'tongoza.storage.WhiteNoiseStaticFilesStorage'

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# TEMP = os.path.join(BASE_DIR, 'media/temp')

BASE_URL = 'http://127.0.0.1:8000/'

if DEBUG:
    # test keys

    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_kEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')

else:
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')

    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME')
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None

    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'


try:
    from tongoza.local_settings import *
except ImportError:
    pass

django_heroku.settings(locals())

if not DEBUG:
    del DATABASES['default']['OPTIONS']['sslmode']