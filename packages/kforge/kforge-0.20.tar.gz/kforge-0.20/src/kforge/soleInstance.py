import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'kforge.django.settings.main'

import kforge.application

application = kforge.application.Application()

