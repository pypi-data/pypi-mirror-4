#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Don't edit this file:
# overload all theses settings in your local_settings.py file

import os

DEBUG = False
TEMPLATE_DEBUG = DEBUG

# Django settings for chimere project.
PROJECT_NAME = u'Chimère'
ROOT_PATH = os.path.realpath(os.path.dirname(__file__)) + "/"

EMAIL_HOST = 'localhost'
STATIC_URL = '/static/'
STATIC_ROOT = ROOT_PATH + 'static/'

TINYMCE_URL = '/tinymce/'
JQUERY_JS_URLS = ('/javascript/jquery/jquery.js',
                  '/javascript/jquery-ui/jquery-ui.js',)
JQUERY_CSS_URLS = ('/javascript/jquery-ui/css/smoothness/jquery-ui.css',
                   '/javascript/jquery-ui-themes/base/jquery.ui.all.css')

OSM_CSS_URLS = ["http://www.openlayers.org/api/theme/default/style.css"]

GPSBABEL = '/usr/bin/gpsbabel'
GPSBABEL_OPTIONS = 'simplify,crosstrack,error=0.005k' # simplify with an
                                                      # error of 5 meters
#GPSBABEL_OPTIONS = 'simplify,count=100'

## chimere specific ##
CHIMERE_DEFAULT_ZOOM = 10
# center of the map
CHIMERE_DEFAULT_CENTER = (-1.679444, 48.114722)
# projection used by the main map
# most public map providers use spherical mercator : 900913
CHIMERE_EPSG_PROJECTION = 900913
# projection displayed to the end user by openlayers
# chimere use the same projection to save its data in the database
CHIMERE_EPSG_DISPLAY_PROJECTION = 4326
# display of shortcuts for areas
CHIMERE_DISPLAY_AREAS = True
# number of day before an event to display
# if equal to 0: disable event management
# if you change this value from 0 to a value in a production environnement
# don't forget to run the upgrade.py script to create appropriate fields in
# the database
CHIMERE_DAYS_BEFORE_EVENT = 30
# allow feeds
CHIMERE_FEEDS = True

CHIMERE_ICON_WIDTH = 21
CHIMERE_ICON_HEIGHT = 25
CHIMERE_ICON_OFFSET_X = -10
CHIMERE_ICON_OFFSET_Y = -25

# display picture inside the description by default or inside a galery?
CHIMERE_MINIATURE_BY_DEFAULT = False

# JS definition of the default map (for admin and when no map are defined in
# the application)
# cf. OpenLayers documentation for more details
CHIMERE_DEFAULT_MAP_LAYER = "new OpenLayers.Layer.OSM.Mapnik('Mapnik')" # OSM mapnik map

CHIMERE_XAPI_URL = 'http://open.mapquestapi.com/xapi/api/0.6/'
CHIMERE_OSM_API_URL = 'api06.dev.openstreetmap.org' # test URL
CHIMERE_OSM_USER = 'test'
CHIMERE_OSM_PASSWORD = 'test'

# as the web server need to be reloaded when property models are changed
# it could be a good idea to hide it to an admin who could'nt do that
CHIMERE_HIDE_PROPERTYMODEL = False

# encoding for shapefile import
CHIMERE_SHAPEFILE_ENCODING = 'ISO-8859-1'

# thumbnail
CHIMERE_THUMBS_SCALE_HEIGHT=250
CHIMERE_THUMBS_SCALE_WIDTH=None

CHIMERE_CSV_ENCODING = 'ISO-8859-1'

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'NAME': 'ratatouille',
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'HOST': 'localhost',
        'PORT': '5432',
        'USER': 'ratatouille',
        'PASSWORD': 'wiki',
    },
}

# Local time zone for this installation. Choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
# although not all variations may be possible on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'fr-fr'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ROOT_PATH + 'media/'

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = '/media/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware'
)

ROOT_URLCONF = 'example_project.urls'

TEMPLATE_DIRS = [
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    ROOT_PATH + 'templates',
    ROOT_PATH + '../chimere/templates',
]

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.gis',
    'django.contrib.staticfiles',
    'south',
    'chimere',
    # activate it if you want to use old migration scripts
    #'chimere.scripts',
]

# celery
try:
    import djcelery
    import kombu
    djcelery.setup_loader()
    BROKER_URL = 'django://'
    INSTALLED_APPS += ['kombu.transport.django',
                       'djcelery']
except ImportError:
    # some import and export will not be available
    pass

INSTALLED_APPS += [
    'south',
    'chimere',
    # activate it if you want to use old migration scripts
    #'chimere.scripts',
]

LOGGING = {'version': 1,
     'disable_existing_loggers': False,
    'handlers': {
        # Include the default Django email handler for errors
        # This is what you'd get without configuring logging at all.
        'mail_admins': {
            'class': 'django.utils.log.AdminEmailHandler',
            'level': 'ERROR',
            # But the emails are plain text by default - HTML is nicer
            'include_html': True,
        },
        # Log to a text file that can be rotated by logrotate
        'logfile': {
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': '/var/log/django/chimere.log'
        },
    },
    'loggers': {
        # Again, default Django configuration to email unhandled exceptions
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        # Might as well log any errors anywhere else in Django
        'django': {
            'handlers': ['logfile'],
            'level': 'ERROR',
            'propagate': False,
        },
        # Your own app - this assumes all your logger names start with "myapp."
        'chimere': {
            'handlers': ['logfile'],
            'level': 'WARNING', # Or maybe INFO or DEBUG
                'propogate': False
        },
    },
}

try:
    from local_settings import *
except ImportError, e:
    print 'Unable to load local_settings.py:', e

if 'CHIMERE_SHARE_NETWORKS' not in globals():
    # after the locals to get the right STATIC_URL

    # share with
    global CHIMERE_SHARE_NETWORKS
    CHIMERE_SHARE_NETWORKS = (
    ("Email", 'mailto:?subject=%(text)s&body=%(url)s',
                 STATIC_URL + 'chimere/img/email.png'),
    ("Facebook", 'http://www.facebook.com/sharer.php?t=%(text)s&u=%(url)s',
                 STATIC_URL + 'chimere/img/facebook.png'),
    ("Twitter", 'http://twitter.com/home?status=%(text)s %(url)s',
                 STATIC_URL + 'chimere/img/twitter.png'),
    ("Identi.ca", 'http://identi.ca/index.php?action=newnotice&status_textarea=%(text)s %(url)s',
                 STATIC_URL + 'chimere/img/identica.png'),
    )

if 'OSM_JS_URLS' not in globals():
    global OSM_JS_URLS
    OSM_JS_URLS = [STATIC_URL + "chimere/js/OpenLayers.js",
                   STATIC_URL + "chimere/js/SimplePanZoom.js",
                   "http://www.openstreetmap.org/openlayers/OpenStreetMap.js"]

