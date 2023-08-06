# -*- coding: utf-8 -*-
"""Base module for unittesting."""

import unittest2 as unittest

from plone.app.controlpanel.tests import ControlPanelTestCase
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.testing import z2
from Products.CMFPlone.tests.utils import MockMailHost
from Products.MailHost.interfaces import IMailHost
from zope.site.hooks import getSite


class NiteowebAweberLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""
        # Load ZCML
        import niteoweb.aweber
        self.loadZCML(package=niteoweb.aweber)
        z2.installProduct(app, 'niteoweb.aweber')

    def setUpPloneSite(self, portal):
        """Set up Plone."""
        # Install into Plone site using portal_setup
        applyProfile(portal, 'niteoweb.aweber:default')

        # Login as Manager
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)

        # Mock mailhost
        portal.email_from_address = 'info@example.org'
        mockmailhost = MockMailHost('MailHost')
        portal.MailHost = mockmailhost
        sm = getSite().getSiteManager()
        sm.registerUtility(component=mockmailhost, provided=IMailHost)

        # Commit so that the test browser sees these objects
        portal.portal_catalog.clearFindAndRebuild()
        import transaction
        transaction.commit()

    def tearDownZope(self, app):
        """Tear down Zope."""
        z2.uninstallProduct(app, 'niteoweb.aweber')


FIXTURE = NiteowebAweberLayer()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,), name="NiteowebAweberLayer:Integration")
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,), name="NiteowebAweberLayer:Functional")


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION_TESTING


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL_TESTING

    def login_as_admin(self):
        # login as admin
        self.browser.open(self.portal.absolute_url() + '/login')
        self.browser.getLink('Log in').click()
        self.browser.getControl(name='__ac_name').value = "admin"
        self.browser.getControl(name='__ac_password').value = \
            TEST_USER_PASSWORD
        self.browser.getControl(name='submit').click()


class AweberControlPanelTestCase(FunctionalTestCase, ControlPanelTestCase):
    """Test case used for control panel tests, with some convenience
    methods from plone.app.controlpanel.
    """
