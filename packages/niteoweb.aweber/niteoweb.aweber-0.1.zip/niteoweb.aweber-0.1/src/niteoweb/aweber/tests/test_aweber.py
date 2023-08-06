# -*- coding: utf-8 -*-
"""Test Aweber methods"""

from mock import Mock
from mock import patch
from niteoweb.aweber import controlpanel
from niteoweb.aweber.interfaces import IAweberSettings
from niteoweb.aweber.testing import FunctionalTestCase
from niteoweb.aweber.testing import IntegrationTestCase
from plone import api
from plone.registry.interfaces import IRegistry
from plone.testing.z2 import Browser
from zope.component import getUtility
from zope.testing.loggingsupport import InstalledHandler

import transaction


class FunctionalTestAweber(FunctionalTestCase):
    """Functional test of Aweber."""

    def setUp(self):
        """Prepare testing environment."""
        self.portal = self.layer['portal']

        self.registry = getUtility(IRegistry)
        self.settings = self.registry.forInterface(IAweberSettings)
        self.settings.app_id = u'appid'
        self.settings.authorization_code = u'authorizationcode'
        self.settings.consumer_key = u'consumerkey'
        self.settings.consumer_secret = u'consumersecret'
        self.settings.access_token = u'accesstoken'
        self.settings.access_secret = u'accesssecret'
        transaction.commit()

        self.browser = Browser(self.portal)
        self.login_as_admin()

        # install a testing log handler
        self.logger = InstalledHandler('niteoweb.aweber')

    def tearDown(self):
        """Clean up after yourself."""

        # logout
        self.browser.open(self.portal.absolute_url() + '/logout')

        # reset our mocked logger
        self.logger.uninstall()
        self.logger.clear()

    def test_controlpanel_view(self):
        """Test for control panel view."""
        self.browser.open(self.portal.absolute_url() + "/@@aweber-settings")
        self.assertEqual(
            self.browser.url,
            'http://nohost/plone/@@aweber-settings',
        )
        self.assertIn(
            '<h1 class="documentFirstHeading">Aweber settings</h1>',
            self.browser.contents,
        )

    def test_save(self):
        """Test save button."""
        self.browser.open(self.portal.absolute_url() + "/@@aweber-settings")
        self.browser.getControl(name='form.widgets.app_id').value = \
            u'temp_app_id'
        self.browser.getControl(name="form.buttons.save").click()

        # test if value is saved
        self.assertEqual(
            self.settings.app_id,
            u'temp_app_id'
        )

    def test_cancel(self):
        """Test cancel button."""
        self.browser.open(self.portal.absolute_url() + "/@@aweber-settings")
        self.browser.getControl(name='form.widgets.app_id').value = \
            u'temp_app_id'
        self.browser.getControl(name="form.buttons.cancel").click()

        # test if value is unchanged
        self.assertEqual(
            self.settings.app_id,
            u'appid'
        )

    def test_get_auth(self):
        """Test get authorization code button."""
        self.browser.open(self.portal.absolute_url() + "/@@aweber-settings")
        self.browser.getControl(name="form.buttons.get_auth").click()

        url = "https://auth.aweber.com/1.0/oauth/authorize_app/{0}".format(
            self.browser.getControl(name="form.widgets.app_id").value
        )
        message = "Visit '{0}' and copy authorization code " \
            "to Authorization Code field".format(url)
        self.assertIn(message, self.browser.contents)

    @patch("niteoweb.aweber.controlpanel.parse_auth_code")
    @patch("niteoweb.aweber.controlpanel.set_list_names")
    def test_parse_auth(self, set_list_names, parse_auth_code):
        """Test get authorization code button."""
        self.browser.open(self.portal.absolute_url() + "/@@aweber-settings")
        self.browser.getControl(name="form.buttons.parse_auth").click()
        assert set_list_names.called
        assert parse_auth_code.called

    @patch("niteoweb.aweber.controlpanel.set_list_names")
    def test_update_lists(self, set_list_names):
        """Test update lists button."""
        self.browser.open(self.portal.absolute_url() + "/@@aweber-settings")
        self.browser.getControl(name="form.buttons.update_lists").click()
        assert set_list_names.called

    @patch("niteoweb.aweber.aweberapi.subscribe_to_aweber_mailinglist")
    def test_subscribe_user(self, subscribe):
        """Test subscribe user button."""
        self.browser.open(self.portal.absolute_url() + "/@@aweber-settings")
        self.browser.getControl(name="form.buttons.subscribe_user").click()
        assert subscribe.called


class IntegrationTestAweber(IntegrationTestCase):
    """Integration test of Aweber."""

    @patch("niteoweb.aweber.controlpanel.AWeberAPI")
    def test_set_list_names(self, mocked_AWeberAPI):
        """Test set list names method."""
        list_names = []
        for i in range(30):
            obj = Mock()
            obj.name = u"listname{0}".format(i)
            list_names.append(obj)

        mocked_AWeberAPI.return_value.get_account.return_value.lists = \
            list_names

        widgets = {
            'consumer_key': Mock(value="consumerkey"),
            'consumer_secret': Mock(value="consumersecret"),
            'access_token': Mock(value="accesstoken"),
            'access_secret': Mock(value="accesssecret")
        }

        controlpanel.set_list_names(widgets)

        available_lists = api.portal.get_registry_record(
            'niteoweb.aweber.available_lists_record',
        )

        assert mocked_AWeberAPI.called
        assert mocked_AWeberAPI.return_value.get_account.called
        assert available_lists == [n.name for n in list_names]

    @patch("niteoweb.aweber.controlpanel.AWeberAPI.parse_authorization_code")
    def test_parse_auth_code(self, mocked_parse):
        """Test parse authorization code method."""
        mocked_parse.return_value = (
            u"new_consumerkey",
            u"new_consumersecret",
            "new_accesstoken",
            "new_accesssecret",
        )

        widgets = {
            'consumer_key': Mock(value="old_consumerkey"),
            'consumer_secret': Mock(value="old_consumersecret"),
            'access_token': Mock(value="old_accesstoken"),
            'access_secret': Mock(value="old_accesssecret"),
            'authorization_code': Mock(value="old_authorizationcode"),
        }

        self.registry = getUtility(IRegistry)
        self.settings = self.registry.forInterface(IAweberSettings)
        self.settings.authorization_code = u'authorizationcode'

        controlpanel.parse_auth_code(widgets)

        self.assertEqual(
            self.settings.consumer_key,
            u"new_consumerkey",
        )
        self.assertEqual(
            self.settings.consumer_secret,
            u"new_consumersecret",
        )
        self.assertEqual(
            self.settings.access_token,
            u"new_accesstoken",
        )
        self.assertEqual(
            self.settings.access_secret,
            u"new_accesssecret",
        )
