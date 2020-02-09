from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

# Raise exceptions when django-crispy-forms encounters an issue
# https://django-crispy-forms.readthedocs.io/en/d-0/tags.html#make-django-crispy-forms-fail-loud
CRISPY_FAIL_SILENTLY = False

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
