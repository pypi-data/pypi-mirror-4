import os
from tempfile import mkdtemp

INSTALLED_APPS = (
    'jqueryfileupload',
)
DATABASE_ENGINE = 'sqlite3'
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3'}}
ROOT_URLCONF = 'tests_urls'
TEMPLATE_DIRS = (
    os.path.dirname(__file__),
)
STATIC_ROOT = mkdtemp()
