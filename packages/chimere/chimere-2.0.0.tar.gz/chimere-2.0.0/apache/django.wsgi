import os, sys
MAIN_PATH = os.path.realpath(os.path.dirname(__file__)) + "/.."
sys.path.append(MAIN_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'mychimere_project.settings' # change with your project name
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
