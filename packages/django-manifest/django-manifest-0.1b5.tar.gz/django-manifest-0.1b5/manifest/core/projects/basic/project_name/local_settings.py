# -*- coding: utf-8 -*-
"""
Django local settings for {{ project_name }} project.
"""

import os
import settings

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

MIDDLEWARE_CLASSES = settings.MIDDLEWARE_CLASSES + (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INSTALLED_APPS = settings.INSTALLED_APPS + (
    'debug_toolbar',
	#'django_extensions',
	#'django_evolution',
)

# Settings for Django Debug Toolbar
INTERNAL_IPS = ('127.0.0.1',)
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
#    'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
#    'EXTRA_SIGNALS': ['{{ project_name }}.signals.MySignal'],
#    'HIDE_DJANGO_SQL': False,
#    'TAG': 'div',
#    'ENABLE_STACKTRACES' : True,
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = True
EMAIL_PORT = 587

DEFAULT_FROM_EMAIL = 'Django Manifest <no-reply@django-manifest.org>'
EMAIL_SUBJECT_PREFIX = '[Django Manifest] '

GOOGLE_ANALYTICS_ACCOUNT    = ''
FACEBOOK_APP_ID             = ''
FACEBOOK_API_SECRET         = ''
