# Copyright 2010 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from django.conf import settings

from .models import REGISTRY

__version__ = "0.1.4"


def autodiscover():
    """Looks for preflight.py modules in the applications."""
    # Import all preflight modules in applications
    for app_name in settings.INSTALLED_APPS:
        try:
            __import__(app_name + '.preflight', {}, {}, [''])
        except ImportError, e:
            msg = e.args[0].lower()
            if 'no module named' not in msg or 'preflight' not in msg:
                raise


class Preflight(object):

    name = "Application Checks"

    def authenticate(self, request):
        return request.user.is_staff


def register(class_):
    if class_ not in REGISTRY:
        REGISTRY.append(class_)
