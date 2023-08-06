# (c) 2012 oeko.net
# c/o toni mueller <support@oeko.net>
# license: GPLv3

import unittest2 as unittest

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import quickInstallProduct
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

import Products.CMFPlone

from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD

#from plone.app.testing import setRoles

from plone.app.testing import applyProfile

from plone.testing import z2
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName

class OnCarouFredSelFixture(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import on.caroufredsel
        self.loadZCML(package=on.caroufredsel)
        self.loadZCML(package=Products.CMFPlone)

    def setUpPloneSite(self, portal):
        wftool = getToolByName(portal, 'portal_workflow')
        wftool.setDefaultChain('folder_workflow')
        """Run the GS profile for this product"""
        self.applyProfile(portal, 'on.caroufredsel:default')
        #import pdb; pdb.set_trace()


    def tearDownZope(self, app):
        """Uninstall the product and destroy the Zope site"""
        z2.uninstallProduct(app, 'on.caroufredsel')

#    def manager_browser(self):
#        """Browser of Manager - not accessible from test layer
#        """
#        return self._auth_browser(SITE_OWNER_NAME, SITE_OWNER_PASSWORD)


ON_CAROUFREDSEL_FIXTURE = OnCarouFredSelFixture()
ON_CAROUFREDSEL_INTEGRATION_TESTING = IntegrationTesting(bases=(ON_CAROUFREDSEL_FIXTURE,), name="OnCarouFredSelFixture:Integration")
ON_CAROUFREDSEL_FUNCTIONAL_TESTING = FunctionalTesting(bases=(ON_CAROUFREDSEL_FIXTURE,), name="OnCarouFredSelFixture:Functional")

