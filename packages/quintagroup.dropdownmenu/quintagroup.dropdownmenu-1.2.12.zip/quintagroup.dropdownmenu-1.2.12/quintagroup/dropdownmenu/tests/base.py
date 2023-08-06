from zope.interface import alsoProvides

from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import setSecurityManager

from Testing import ZopeTestCase as ztc
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc

from collective.testcaselayer.ptc import BasePTCLayer, ptc_layer


from quintagroup.dropdownmenu import PROJECT_NAME
from quintagroup.dropdownmenu.interfaces import IDropDownMenuLayer

IPREFIX = 'quintagroup.dropdownmenu.interfaces.IDropDownMenuSettings.'

# This step made in collective.testcaselayer.ptc
#ptc.setupPloneSite()


class NotInstalled(BasePTCLayer):
    """Initialize the package, without installation into portal
    """
    def afterSetUp(self):
        fiveconfigure.debug_mode = True
        import quintagroup.dropdownmenu
        self.loadZCML('configure.zcml', package=quintagroup.dropdownmenu)
        fiveconfigure.debug_mode = False
        ztc.installPackage(PROJECT_NAME)


class Installed(BasePTCLayer):
    """ Install product into the portal
    """
    def afterSetUp(self):
        self.addProduct(PROJECT_NAME)


class UnInstalled(BasePTCLayer):
    """ UnInstall product from the portal
    """
    def afterSetUp(self):
        sm = getSecurityManager()
        self.loginAsPortalOwner()
        try:
            qi = self.portal.portal_quickinstaller
            qi.uninstallProducts(products=[PROJECT_NAME, ])
            #self._refreshSkinData()
        finally:
            setSecurityManager(sm)

NotInstalledLayer = NotInstalled([ptc_layer, ])
InstalledLayer = Installed([NotInstalledLayer, ])
UnInstalledLayer = UnInstalled([InstalledLayer, ])


class TestCaseNotInstalled(ptc.PloneTestCase):
    layer = NotInstalledLayer


class TestCase(ptc.PloneTestCase):
    layer = InstalledLayer

    def afterSetUp(self):
        # mark request with our browser layer
        super(TestCase, self).afterSetUp()
        alsoProvides(self.app.REQUEST, IDropDownMenuLayer)


class TestCaseUnInstalled(ptc.PloneTestCase):
    layer = UnInstalledLayer


class FunctionalTestCaseNotInstalled(ptc.FunctionalTestCase):
    layer = NotInstalledLayer


class FunctionalTestCase(ptc.FunctionalTestCase):
    layer = InstalledLayer

    def afterSetUp(self):
        # mark request with our browser layer
        super(FunctionalTestCase, self).afterSetUp()
        alsoProvides(self.app.REQUEST, IDropDownMenuLayer)


class FunctionalTestCaseUnInstalled(ptc.FunctionalTestCase):
    layer = UnInstalledLayer
