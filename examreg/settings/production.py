from .base import *
import psycopg2

DEBUG = False

ALLOWED_HOSTS = ['exams.ugrad.cs.cmu.edu']


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

FORCE_SCRIPT_NAME = '/213/examreg/'
STATIC_URL = FORCE_SCRIPT_NAME + 'static/'
LOGIN_URL = FORCE_SCRIPT_NAME + 'accounts/login/'
LOGOUT_URL = FORCE_SCRIPT_NAME + 'accounts/logout/'

STATIC_ROOT = '/usr0/www/html/examreg/'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'examreg',
        'USER': config('POSTGRES_DB_USER'),
        'PASSWORD': config('POSTGRES_DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '',
        'OPTIONS': {
            'isolation_level': psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE,
        },
    }
}


# Security middleware settings
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'

SILENCED_SYSTEM_CHECKS = [
    'security.W004',  # HSTS header not set
]
