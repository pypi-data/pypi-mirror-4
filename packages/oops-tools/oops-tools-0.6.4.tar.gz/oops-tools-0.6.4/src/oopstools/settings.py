# Django settings for oopstools project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'lpoops',
        'USER': 'lpoops',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '5433'
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '12345'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'timeline_django.middleware.TimelineMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'oopstools.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    "/home/robertc/source/launchpad/oops-tools/working/src/oopstools/oops/templates/"
    "/home/robertc/source/launchpad/oops-tools/working/parts/django/django/contrib/admin/templates/admin/"
)

TEST_RUNNER = 'oopstools.oops.test.test_runner.CustomTestRunner'

import os

ROOT = "/home/robertc/source/launchpad/oops-tools/working"
BIN_DIR = "/home/robertc/source/launchpad/oops-tools/working/bin"

ROOT_URL = "http://localhost:8000"

LAZR_CONFIG = "/home/robertc/source/launchpad/oops-tools/working/src/oopstools/oops/test/files/lazr-configs/"

STATIC_DOC_ROOT = os.path.join(ROOT, 'src', 'oopstools', 'oops', 'static')

# XXX: If we could get this in a convenient format from
# z3c.recipe.filetemplate it would be better.
paths = """
    /home/robertc/source/launchpad/oops-tools/working/src/oopstools/oops/test/files/oops-sample
/var/tmp/lperr
"""
OOPSDIR = [path.strip() for path in paths.split()]

INDEX_TEMPLATE = "index.html"

SUMMARY_URI = "https://example.com/oops-summaries"
SUMMARY_DIR = "/tmp/oops-summaries/"
# Deprecated: set in the report admin UI instead.
REPORT_TO_ADDRESS = "test@example.com"
REPORT_FROM_ADDRESS = "test@example.com"

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'oopstools.oops',
    'south'
)

OOPS_WEB_AMQP_HOST = 'localhost'
OOPS_WEB_AMQP_USER = 'guest'
OOPS_WEB_AMQP_PASSWORD = 'guest'
OOPS_WEB_AMQP_VHOST = '/'
OOPS_WEB_AMQP_EXCHANGE = 'oopses'
OOPS_WEB_AMQP_ROUTING = ''
