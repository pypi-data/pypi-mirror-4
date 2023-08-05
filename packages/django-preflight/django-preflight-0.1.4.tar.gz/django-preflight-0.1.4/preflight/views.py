# Copyright 2010 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from datetime import datetime

from django.views.decorators.cache import never_cache
from django.http import Http404
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext

from .models import (
    authenticate,
    gather_checks,
    gather_settings,
    gather_versions,
)

@never_cache
def overview(request):
    if not authenticate(request):
        raise Http404

    base_template = getattr(settings, 'PREFLIGHT_BASE_TEMPLATE',
                            "admin/base.html")
    table_class = getattr(settings, 'PREFLIGHT_TABLE_CLASS', "listing")

    context = RequestContext(request, {
        "applications": gather_checks(),
        "versions": gather_versions(),
        "settings": gather_settings(),
        "now": datetime.now(),
        "preflight_base_template": base_template,
        'preflight_table_class': table_class,
    })
    return render_to_response("preflight/overview.html", context)
