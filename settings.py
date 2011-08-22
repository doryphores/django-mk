import os

PROJECT_ROOT = os.path.dirname(__file__)

# Django settings for django_mk project.

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
	# ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
		'NAME': os.path.join(PROJECT_ROOT, "db.sqlite"),					  # Or path to database file if using sqlite3.
		'USER': '',					  # Not used with sqlite3.
		'PASSWORD': '',				  # Not used with sqlite3.
		'HOST': '',					  # Set to empty string for localhost. Not used with sqlite3.
		'PORT': '',					  # Set to empty string for default. Not used with sqlite3.
	}
}

INTERNAL_IPS=('127.0.0.1', '192.168.0.4')

# Cache config
CACHE_BACKEND = 'memcached://127.0.0.1:11211/'


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/London'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, "public", "media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, "public", "static")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
STATIC_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'y&8alk18xnzfp_g16ttdv9md%*#&jx9wjp)7_1xrg0ds9puy4w'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
	'django.template.loaders.filesystem.Loader',
	'django.template.loaders.app_directories.Loader',
#	 'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.transaction.TransactionMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
	# Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
	# Always use forward slashes, even on Windows.
	# Don't forget to use absolute paths, not relative paths.
	os.path.join(PROJECT_ROOT, "templates")
)

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

SESSION_SAVE_EVERY_REQUEST = True

SESSION_COOKIE_AGE = 10800 # 3 Hours

INSTALLED_APPS = (
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sites',
	'django.contrib.messages',
	'django.contrib.admin',
	'django.contrib.staticfiles',
	# Uncomment the next line to enable admin documentation:
	# 'django.contrib.admindocs',
	'app',
	'south',
)

try:
	import local_settings
except ImportError:
	pass
	#===========================================================================
	# print """ 
	#	-------------------------------------------------------------------------
	#	You need to create a local_settings.py file which needs to contain at least
	#	database connection information.
	#	
	#	Copy local_settings_example.py to local_settings.py and edit it.
	#	-------------------------------------------------------------------------
	#	"""
	# import sys 
	# sys.exit(1)
	#===========================================================================
else:
	# Import any symbols that begin with A-Z. Append to lists any symbols that
	# begin with "EXTRA_".
	import re
	for attr in dir(local_settings):
		match = re.search('^EXTRA_(\w+)', attr)
		if match:
			name = match.group(1)
			value = getattr(local_settings, attr)
			try:
				globals()[name] += value
			except KeyError:
				globals()[name] = value
		elif re.search('^[A-Z]', attr):
			globals()[attr] = getattr(local_settings, attr)