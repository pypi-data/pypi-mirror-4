import logging
from Products.CMFCore.utils import getToolByName

from quintagroup.dropdownmenu import PROJECT_NAME

logger = logging.getLogger('quintagroup.dropdownmenu')

UNINSTALL = "profile-%s:uninstall" % PROJECT_NAME


def uninstall(portal, reinstall=False):
    """ Uninstall this product.

        This external method is need, because portal_quickinstaller doens't
        know what GenericProfile profile to apply when uninstalling a product.
    """
    setup_tool = getToolByName(portal, 'portal_setup')
    if reinstall:
        return "Ran all reinstall steps."
    else:
        setup_tool.runAllImportStepsFromProfile(UNINSTALL)
        return "Ran all uninstall steps."
