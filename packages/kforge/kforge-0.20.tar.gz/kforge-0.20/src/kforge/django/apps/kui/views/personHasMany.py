from dm.view.base import *
from kforge.django.apps.kui.views.person import PersonInstanceView
import kforge.command
from kforge.exceptions import KforgeCommandError


class PersonHasManyView(AbstractHasManyView, PersonInstanceView):

    pass


