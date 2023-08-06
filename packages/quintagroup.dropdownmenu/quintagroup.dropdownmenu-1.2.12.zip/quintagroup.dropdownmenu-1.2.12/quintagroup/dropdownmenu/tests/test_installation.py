#
# Test product's installation
#
from zope.component import queryUtility
from plone.registry.interfaces import IRegistry
from plone.browserlayer import utils as blutils

from Products.CMFCore.utils import getToolByName

from quintagroup.dropdownmenu.tests.base import TestCase, TestCaseUnInstalled
from quintagroup.dropdownmenu.tests.base import IPREFIX

from quintagroup.dropdownmenu import PROJECT_NAME
from quintagroup.dropdownmenu.interfaces import IDropDownMenuLayer

CSS_RESOURCES = ["++resource++drop_down.css", ]
DEPENDENCIES = ["plone.app.registry", ]
CONFIGLETS = ["dropdownmenu", ]
#REGISTRY_INTERFACE="quintagroup.dropdownmenu.interfaces.IDropDownMenuSettings"


class TestInstallation(TestCase):

    def testInstalled(self):
        qi = self.portal.portal_quickinstaller
        self.assertTrue(qi.isProductInstalled(PROJECT_NAME),
                        '%s is not installed.' % PROJECT_NAME)

    def testInstalledDependencies(self):
        cp = self.portal.portal_controlpanel
        configlets = [ai['id'] for ai in cp.listActionInfos(
                      check_permissions=0)]
        self.assertTrue([1 for ai in configlets if ai == "plone.app.registry"],
                        'Not installed required plone.app.registry product.')

    def testStyles(self):
        """ Test styles registration."""
        cssreg = getToolByName(self.portal, "portal_css")
        for res in CSS_RESOURCES:
            self.assertNotEqual(cssreg.getResource(res), None)

    def testConfiglet(self):
        cp = self.portal.portal_controlpanel
        configlets = [ai['id'] for ai in cp.listActionInfos(
                      check_permissions=0)]
        for cid in CONFIGLETS:
            self.assertTrue([
                1 for ai in configlets if ai == cid],
                'No "%s" configlet added to plone control panel' % cid)

    def testBrowserLayer(self):
        self.assert_(IDropDownMenuLayer in blutils.registered_layers(),
                     "Not registered 'IDropDownMenuLayer' browser layer")

    def testRegistry(self):
        registry = queryUtility(IRegistry)
        afield = "show_content_tabs"
        self.assertTrue(registry.records.get(IPREFIX + afield, None),
                        "Not registered '%s' registry interface" % IPREFIX)


class TestUninstallation(TestCaseUnInstalled):

    def testUninstalled(self):
        qi = self.portal.portal_quickinstaller
        self.assertFalse(qi.isProductInstalled(PROJECT_NAME),
                         '%s not uninstalled.' % PROJECT_NAME)

    def testStyles(self):
        """ Test styles registration."""
        cssreg = getToolByName(self.portal, "portal_css")
        for res in CSS_RESOURCES:
            self.assertEqual(cssreg.getResource(res), None)

    def testConfiglet(self):
        cp = self.portal.portal_controlpanel
        configlets = [ai['id'] for ai in cp.listActionInfos(
                      check_permissions=0)]
        for cid in CONFIGLETS:
            self.assertFalse([1 for ai in configlets if ai == cid],
                             '"%s" configlet not uninstalled '
                             'from plone control panel' % cid)

    def testBrowserLayer(self):
        self.assertFalse(IDropDownMenuLayer in blutils.registered_layers(),
                         "Not unregistered 'IDropDownMenuLayer' browser layer")

    def testRegistry(self):
        registry = queryUtility(IRegistry)
        afield = "show_content_tabs"
        self.assertFalse(registry.records.get(IPREFIX + afield, None),
                         "Not unregistered '%s' registry interface" % IPREFIX)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestInstallation))
    suite.addTest(makeSuite(TestUninstallation))
    return suite
