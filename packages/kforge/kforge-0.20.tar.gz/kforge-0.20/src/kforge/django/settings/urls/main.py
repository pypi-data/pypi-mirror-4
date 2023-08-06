from django.conf.urls.defaults import *
from kforge.soleInstance import application
from kforge.dictionarywords import URI_PREFIX

import os
# Mod_python passes the prefix in the path. Mod_wsgi doesn't.
uriPrefixPattern = ''
if 'RUNNING_IN_MOD_PYTHON' in os.environ:
    uriPrefix = application.dictionary[URI_PREFIX]
    if uriPrefix:
        uriPrefixPattern = uriPrefix.lstrip('/') + '/'

urlpatterns = patterns('',
    (
        r'^%s' % uriPrefixPattern, include('kforge.django.settings.urls.kui')
    ),
)
