
import unittest2 as unittest

#from zope.component import queryUtility

from Products.CMFCore.utils import getToolByName

from plone.registry.interfaces import IRegistry
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from on.caroufredsel.testing import ON_CAROUFREDSEL_INTEGRATION_TESTING


class TestLibInRegistry(unittest.TestCase):
    """Test the integration of the product."""

    layer = ON_CAROUFREDSEL_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_can_we_find_the_library(self):
        """Get the registry and see whether we have this lib listed."""
        tool = getToolByName(self.portal, "portal_javascripts")
        self.assertNotEqual(tool, None)
        installedScriptIds = tool.getResourceIds()
        #import pdb; pdb.set_trace()
        self.assertTrue("++resource++on.caroufredsel.js" in installedScriptIds, "on.caroufredsel.js")
        self.assertTrue("++resource++on.caroufredsel-compact.js" in installedScriptIds, "on.caroufredsel-compact.js")
