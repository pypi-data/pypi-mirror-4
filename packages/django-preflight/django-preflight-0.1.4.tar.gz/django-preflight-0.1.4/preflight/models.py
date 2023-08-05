# Copyright 2010 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from __future__ import absolute_import

import re
from django.conf import settings
from django.views.debug import HIDDEN_SETTINGS

REGISTRY = []


class Application(object):

    def __init__(self, class_):
        self.class_ = class_
        self.checks = []
        self.name = "%s checks" % self._application_name()
        self._gather_checks()

    def _gather_checks(self):
        check_names = (s for s in sorted(dir(self.class_))
                       if s.startswith('check_'))
        for check_name in check_names:
            instance = self.class_()
            bound_method = getattr(instance, check_name)
            check = Check(check_name[len('check_'):], bound_method)
            check.check()
            self.checks.append(check)

    def _application_name(self):
        return '.'.join(self.class_.__module__.split('.')[:-1])

    @property
    def passed(self):
        return all(check.passed for check in self.checks)


class Check(object):

    """
    Representation of one check performed and place to store its result.
    """

    def __init__(self, name, bound_method):
        self.name = name
        self.bound_method = bound_method
        self.description = self.bound_method.__doc__
        if self.description is None:
            self.description = ""

    def check(self):
        """
        Returns True if check was successful and False otherwise.

        This result is also stored in object's attribute ``passed``.
        """
        try:
            self.passed = bool(self.bound_method())
        except Exception, exc:
            self.exception = unicode(exc)
            self.passed = False
        return self.passed


def gather_checks():
    applications = []
    for class_ in REGISTRY:
        application = Application(class_)
        applications.append(application)
    return applications


def gather_versions():
    """
    Gather list of version information to be displayed alongside the checks
    data.

    """
    import platform
    import sys
    import django
    import preflight

    items = [
        {'name': 'Platform', 'version': platform.platform()},
        {'name': 'Django', 'version': django.get_version()},
        {'name': 'Python', 'version': sys.version},
        {'name': 'preflight', 'version': preflight.__version__}
    ]

    for class_ in REGISTRY:
        if hasattr(class_, 'versions'):
            instance = class_()
            if callable(instance.versions):
                items.extend(class_().versions())
            else:
                for item in class_().versions:
                    items.append(item)

    return items


def locate_setting(key):
    try:
        parser = settings.__CONFIGGLUE_PARSER__
    except AttributeError:
        return ''
    cases = [key, key.lower(), key.upper()]
    for case in cases:
        location = parser.locate(option=case)
        if location is not None:
            return location
    else:
        return "not found"


def gather_settings():
    names = sorted([x for x in settings._wrapped.__dict__
        if x.isupper() and not x.startswith('_')])
    settings_list = []
    hidden_settings = getattr(settings, 'PREFLIGHT_HIDDEN_SETTINGS', None)
    if hidden_settings:
        hidden_settings = re.compile(hidden_settings)
    else:
        hidden_settings = HIDDEN_SETTINGS
    for name in names:
        if HIDDEN_SETTINGS.match(name):
            value = '******************'
        else:
            value = getattr(settings, name, None)
        settings_list.append({
            'name': name,
            'value': value,
            'location': locate_setting(name),
        })
    return settings_list


def authenticate(request):
    """
    To be able to access you need to have permission from every preflight class.
    """
    return all(class_().authenticate(request) for class_ in REGISTRY)
