import os, sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'kforge.django.settings.main'
from django.core.handlers.wsgi import WSGIHandler
