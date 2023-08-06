# Django settings for KForge Web interface.
from django.dispatch import dispatcher
from django.core import signals
from kforge.soleInstance import application
from dm.django.settings.main import *
import os

ROOT_URLCONF = 'kforge.django.settings.urls.main'

# Set the umask for the duration of each request.
class UmaskSetter(object):
    def __init__(self, umask):
        # Todo: Assert type of umask parameter equals int?
        self._requestUmask = umask
        self._oldUmask = None

    def beginRequest(self, **kwds):
        if type(self._requestUmask) == int:
            try:
                self._oldUmask = os.umask(self._requestUmask)
            except:
                # Todo: Log a warning about this?
                pass


    def endRequest(self, **kwds):
        if type(self._oldUmask) == int:
            try:
                os.umask(self._oldUmask)
            except:
                # Todo: Log a warning about this?
                pass
        else:
            # Todo: Log a warning about this?
            pass
        self._oldUmask = None


umaskSetter = UmaskSetter(application.dictionary.getUmask())
if not hasattr(dispatcher, 'connect'):  # Django 1.0.
    signals.request_started.connect(umaskSetter.beginRequest)
    signals.request_finished.connect(umaskSetter.endRequest)
else:                                   # Django 0.96.
    dispatcher.connect(umaskSetter.beginRequest, signal=signals.request_started)
    dispatcher.connect(umaskSetter.endRequest, signal=signals.request_finished)
