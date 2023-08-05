#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

DEBUG = True

HOST = "localhost"
#HOST = "192.168.1.200"

SERVER_URL = 'http://'+HOST+':8000/'
EXTRA_URL = ''
STATIC_URL = 'http://'+HOST+'/chimere/static/'

# Make this string unique, and don't share it with anybody.
SECRET_KEY = ''

TINYMCE_URL = '/tinymce/'
TINYMCE_URL = 'http://'+HOST+'/' + TINYMCE_URL
JQUERY_CSS_URLS = ('/javascript/jquery-ui/css/smoothness/jquery-ui.css',
                   '/javascript/jquery-ui-themes/south-street/jquery.ui.all.css')
JQUERY_JS_URLS = ('/javascript/jquery/jquery.js',
                  '/javascript/jquery-ui/jquery-ui.js',)
JQUERY_JS_URLS = ['http://'+HOST+'' + url for url in JQUERY_JS_URLS]
JQUERY_CSS_URLS = ('/javascript/jquery-ui/css/smoothness/jquery-ui.css',
                   '/javascript/jquery-ui-themes/base/jquery.ui.all.css')
JQUERY_CSS_URLS = ['http://'+HOST+'' + url for url in JQUERY_CSS_URLS]

OSM_CSS_URLS = ['http://'+HOST+'/style_osm.css']
OSM_JS_URLS = ['http://'+HOST+'/chimere/static/' + "chimere/js/OpenLayers.js",
               'http://'+HOST+'/chimere/static/' + "chimere/js/SimplePanZoom.js",
               'http://'+HOST+'/OpenStreetMap.js']


CHIMERE_OSM_API_URL = 'api06.dev.openstreetmap.org' # test URL
CHIMERE_OSM_USER = 'etienne.loks@peacefrogs.net'
CHIMERE_OSM_PASSWORD = u'mélusine'

# enable routing in Chimère
CHIMERE_ENABLE_ROUTING = True

CHIMERE_ROUTING_ENGINE = {
    'ENGINE': 'routino',
    'PATH': '/home/nim/Work/chimere-project/routino/routino-2.3/web/bin/router',
    'DB_PATH': '/var/local/routino/',
}


ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

db_name = 'chimere'
db_name = 'chimere_test'

DATABASES = {
    'default': {
        'NAME': db_name,
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'HOST': '',
        'PORT': '5432',
        'USER': 'postgres',
        'PASSWORD': '',
    },
}
# URL that handles the media served from MEDIA_ROOT.
MEDIA_URL = 'http://'+HOST+'/chimere/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
ADMIN_MEDIA_PREFIX = 'http://'+HOST+'/admin-media/'


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


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
            'filename': '/tmp/chimere.log'
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
        'main': {
            'handlers': ['logfile'],
            'level': 'WARNING', # Or maybe INFO or DEBUG
                'propogate': False
        },
    },
}

