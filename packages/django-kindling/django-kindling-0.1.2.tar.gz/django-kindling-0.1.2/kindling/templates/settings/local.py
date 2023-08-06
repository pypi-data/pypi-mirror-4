from .development import *


DATABASES['default']['NAME'] = '{{ app }}'
DATABASES['default']['USER'] = '{{ app }}'
DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql_psycopg2'
DATABASES['default']['OPTIONS'] = {
    'autocommit': True,
}
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'