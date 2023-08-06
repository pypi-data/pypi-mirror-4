from base import *
DEBUG = True
INSTALLED_APPS += (
    'django_nose',
)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        'JOHNNY_CACHE': True,
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'tests.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
NOSE_ARGS = ['--verbosity', '1']
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
CELERY_ALWAYS_EAGER = True
