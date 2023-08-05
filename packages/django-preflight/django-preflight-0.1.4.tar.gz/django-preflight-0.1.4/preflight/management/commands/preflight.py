# Copyright 2010 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from __future__ import absolute_import

import os
import sys


from django.core.management.base import NoArgsCommand
from django.utils import termcolors

from preflight.models import gather_checks
from preflight import autodiscover


class Command(NoArgsCommand):

    help = "Execute all pre-flight checks and report the results"


    def handle_noargs(self, **options):
        error_style = termcolors.make_style(fg='red')
        ok_style = termcolors.make_style(fg='green')
        app_style = termcolors.make_style(fg='white')

        # Compatibility with future Django version which will provide this
        # attribute for every Command instance
        if not hasattr(self, 'stdout'):
            self.stdout = sys.stdout

        # Used for calculating proper output width
        columns = int(os.environ.get('COLUMNS', 80))

        autodiscover()

        # Result page header
        self.stdout.write("Pre-flight checks for applications\n")
        self.stdout.write("=" * columns + '\n')

        applications = gather_checks()

        for application in applications:
            # Separation between applications
            self.stdout.write('\n')

            # Displaying application name in white
            self.stdout.write(app_style(application.name) + '\n')
            self.stdout.write("-" * columns + '\n')

            for check in application.checks:
                # Formatting check result line, uses ANSI colors to prettify it
                if check.passed:
                    status_name = ok_style(" OK")
                else:
                    status_name = error_style("ERROR")

                self.stdout.write(check.name.ljust(columns - 7) + status_name + '\n')

        # Report correct return code to the shell
        sys.exit(not all(a.passed for a in applications))
