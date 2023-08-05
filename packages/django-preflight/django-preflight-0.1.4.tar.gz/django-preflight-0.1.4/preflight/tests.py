# Copyright 2010 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).
import sys

from django.core.management import call_command
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.test import TestCase
from django.template import RequestContext, TemplateDoesNotExist
from mock import (
    Mock,
    patch,
)

from cStringIO import StringIO

from . import Preflight
from .models import (
    Application, 
    Check,
    REGISTRY,
    authenticate,
    gather_checks,
    gather_settings,
    gather_versions,
)



class CheckTestCase(TestCase):

    def setUp(self):
        self.exception = None
        self.return_value = True

    def check_method(self):
        "description"
        if self.exception:
            raise self.exception
        return self.return_value

    def test_initialisation(self):
        check = Check("check_name", self.check_method)

        self.assertEquals(check.name, "check_name")
        self.assertEquals(check.description, "description")

    def test_initialisation_when_doc_is_none(self):
        def method(): pass

        check = Check("check_name", method)

        self.assertEquals(check.description, "")

    def test_check_when_check_method_returns_true(self):
        check = Check("check_name", self.check_method)
        check.check()

        self.assertTrue(check.passed)

    def test_check_when_check_method_returns_false(self):
        self.return_value = False
        check = Check("check_name", self.check_method)
        check.check()

        self.assertFalse(check.passed)

    def test_check_when_check_method_raises_an_exception(self):
        self.exception = Exception("error")
        check = Check("check_name", self.check_method)
        check.check()

        self.assertFalse(check.passed)

    def test_check_returns_right_return_value(self):
        check = Check("check_name", self.check_method)

        self.assertEquals(check.check(), check.passed)

    def test_check_after_exception_has_exception_attribute(self):
        self.exception = Exception("error")
        check = Check("check_name", self.check_method)
        check.check()

        self.assertTrue("error" in check.exception)


class DummyPreflight(Preflight):

    fail = True

    def should_fail(self):
        return self.fail

    def check_success(self):
        return True

    def check_check_test(self):
        return True

    def check_maybe_fail(self):
        return not self.should_fail()


class ApplicationTestCase(TestCase):

    def test_initialisation(self):
        app = Application(DummyPreflight)

        self.assertEqual(app.name, "preflight checks")
        self.assertEqual(len(app.checks), 3)

    def test_check_name_is_properly_handled(self):
        app = Application(DummyPreflight)

        self.assertEqual(set(c.name for c in app.checks),
                         set(['success', 'check_test', 'maybe_fail']))

    def test_check_sets_passed_to_false_if_at_least_one_of_check_fails(self):
        app = Application(DummyPreflight)

        self.assertFalse(app.passed)

    def test_check_sets_passed_to_true_if_all_checks_passed(self):
        DummyPreflight.fail = False

        app = Application(DummyPreflight)

        self.assertTrue(app.passed)

        DummyPreflight.fail = True


class AuthenticatePass(Preflight):

    def authenticate(self, request):
        return True


class AuthenticateFail(Preflight):

    def authenticate(self, request):
        return False

def clear_registry():
    while REGISTRY:
        REGISTRY.pop()


class AutenticateTestCase(TestCase):

    def test_passes_if_all_classes_authenticate_passes(self):
        clear_registry()
        REGISTRY.append(AuthenticatePass)
        REGISTRY.append(AuthenticatePass)

        self.assertTrue(authenticate(None))

    def test_fails_if_at_least_one_class_authenticate_fails(self):
        clear_registry()
        REGISTRY.append(AuthenticatePass)
        REGISTRY.append(AuthenticateFail)

        self.assertFalse(authenticate(None))


class GatherChecksTestCase(TestCase):

    def test(self):
        clear_registry()
        REGISTRY.append(AuthenticatePass)
        REGISTRY.append(AuthenticatePass)
        REGISTRY.append(AuthenticateFail)

        applications = gather_checks()

        self.assertEquals(len(applications), 3)


class ExtraVersionAsCallable(Preflight):

    def versions(self):
        return [{'name': 'spam', 'version': 'ni'}]

class ExtraVersionAsList(Preflight):

    versions = [{'name': 'eggs', 'version': 'peng'}]


class GatherVersions(TestCase):

    def test_default_versions(self):
        clear_registry()

        versions = gather_versions()

        self.assertEquals(len(versions), 4)
        for item in versions:
            self.assertTrue('name' in item and 'version' in item)

    def test_get_extra_version_information_from_checks_class_method(self):
        clear_registry()
        REGISTRY.append(ExtraVersionAsCallable)

        versions = gather_versions()

        self.assertEquals(len(versions), 5)
        self.assertEquals(versions[-1]['name'], 'spam')

    def test_get_extra_version_information_from_class_attribute(self):
        clear_registry()
        REGISTRY.append(ExtraVersionAsList)

        versions = gather_versions()

        self.assertEquals(len(versions), 5)
        self.assertEquals(versions[-1]['version'], 'peng')


class PreflightCommandTestCase(TestCase):

    @patch('sys.exit')
    @patch.object(DummyPreflight, 'fail', new=False)
    def test(self, mock_exit):
        clear_registry()
        try:
            sys.stdout = StringIO()
            REGISTRY.append(DummyPreflight)

            call_command('preflight')

            self.assertTrue('checks for applications' in sys.stdout.getvalue())
        finally:
            sys.stdout = sys.__stdout__


class OverviewView(TestCase):
    @patch('preflight.views.authenticate')
    def test_overview_when_not_authenticated(self, mock_authenticate):
        mock_authenticate.return_value = False

        self.assertRaises(TemplateDoesNotExist, self.client.get,
            reverse('preflight-overview'))

    @patch('preflight.views.render_to_response')
    @patch('preflight.views.authenticate')
    def test_overview(self, mock_authenticate, mock_render_to_response):
        mock_authenticate.return_value = True
        mock_render_to_response.return_value = HttpResponse()

        self.client.get(reverse('preflight-overview'))

        mock_render_to_response.assert_called_once()
        context = mock_render_to_response.call_args[0][1]
        self.assertTrue(isinstance(context, RequestContext))


class SettingsTestCase(TestCase):
    @patch('preflight.models.settings')
    def test_gather_settings_no_location(self, mock_settings):
        mock_settings._wrapped.FOO = 'bar'
        mock_settings.FOO = 'bar'
        mock_settings.PREFLIGHT_HIDDEN_SETTINGS = ''
        settings = gather_settings()
        expected = [{'name': 'FOO', 'value': 'bar', 'location': ''}]
        self.assertEqual(expected, settings)

    @patch('preflight.models.settings')
    def test_gather_settings_with_location(self, mock_settings):
        mock_settings._wrapped.FOO = 'bar'
        mock_settings.FOO = 'bar'
        mock_settings.PREFLIGHT_HIDDEN_SETTINGS = ''
        parser = Mock()
        parser.locate.return_value = '/tmp/baz'
        mock_settings.__CONFIGGLUE_PARSER__ = parser
        settings = gather_settings()
        expected = [{'name': 'FOO', 'value': 'bar', 'location': '/tmp/baz'}]
        self.assertEqual(expected, settings)

    @patch('preflight.models.settings')
    def test_gather_settings_hidden(self, mock_settings):
        mock_settings._wrapped.SECRET_FOO = 'bar'
        mock_settings.SECRET_FOO = 'bar'
        mock_settings.PREFLIGHT_HIDDEN_SETTINGS = 'SECRET'
        settings = gather_settings()
        expected = [{'name': 'SECRET_FOO', 'value': '*' * 18, 'location': ''}]
        self.assertEqual(expected, settings)

    @patch('preflight.models.settings')
    def test_gather_settings_omitted(self, mock_settings):
        mock_settings._wrapped._FOO = 'bar'
        mock_settings._FOO = 'bar'
        mock_settings.PREFLIGHT_HIDDEN_SETTINGS = ''
        settings = gather_settings()
        self.assertEqual([], settings)
