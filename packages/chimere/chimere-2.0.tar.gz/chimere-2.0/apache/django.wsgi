import os, sys
sys.path.append('/var/local/django/chimere/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'mychimere_project.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
