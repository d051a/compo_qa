from pathlib import Path
import os
from celery.schedules import crontab

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'bb68r9%%!01d8z6zz&3*4$1437l9(ydit+o@8m9qd10q0c&rva'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(os.environ.get("DEBUG", default=1))

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", '127.0.0.1').split(" ")

DATA_UPLOAD_MAX_NUMBER_FIELDS = 100000
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'conf.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
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

WSGI_APPLICATION = 'conf.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("SQL_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("SQL_DATABASE", os.path.join(BASE_DIR, "db.sqlite3")),
        "USER": os.environ.get("SQL_USER", "user"),
        "PASSWORD": os.environ.get("SQL_PASSWORD", "password"),
        "HOST": os.environ.get("SQL_HOST", "localhost"),
        "PORT": os.environ.get("SQL_PORT", "5432"),
    }
}

# DATABASES = {
#     'default': {
#         'NAME': 'compo_db_dev',
#         'ENGINE': 'django.db.backends.postgresql',
#         'USER': 'compo',
#         'PASSWORD': 'password',
#         'HOST': 'db',
#         'PORT': '5432',
#      },
# }


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


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'ru-RU'
# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_L10N = True
USE_TZ = False

DATETIME_FORMAT = "%d.%m.%Y %H:%M:%S"


STATIC_URL = '/staticfiles/'
MEDIA_URL = '/mediafiles/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles/')
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles/")

STATICFILES_DIRS = (
    ("base_css", os.path.join(BASE_DIR, 'static/base/css')),
    ("base_js", os.path.join(BASE_DIR, 'static/base/js')),
    ("base_fonts", os.path.join(BASE_DIR, 'static/base/fonts')),
    ("base_svg", os.path.join(BASE_DIR, 'static/base/svg')),
    ("base_imgs", os.path.join(BASE_DIR, 'static/base/imgs')),
)

REDIS_HOST = os.environ.get("REDIS_HOST", '0.0.0.0')
REDIS_PORT = os.environ.get("REDIS_PORT", '6379')
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER", "redis://0.0.0.0:6379/0")
CELERY_BROKER_TRANSPORT_OPTIONS = os.environ.get("CELERY_BROKER_TRANSPORT_OPTIONS", {'visibility_timeout': 3600})
CELERY_RESULT_BACKEND = os.environ.get("CELERY_BROKER", "redis://0.0.0.0:6379/0")
CELERY_ACCEPT_CONTENT = os.environ.get("CELERY_ACCEPT_CONTENT", ['application/json'])
CELERY_TASK_SERIALIZER = os.environ.get("CELERY_TASK_SERIALIZER", 'json')
CELERY_RESULT_SERIALIZER = os.environ.get("CELERY_RESULT_SERIALIZER", 'json')