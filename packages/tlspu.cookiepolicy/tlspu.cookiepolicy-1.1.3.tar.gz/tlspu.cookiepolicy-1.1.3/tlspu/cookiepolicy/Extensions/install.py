import logging
from Products.CMFCore.utils import getToolByName

logger = logging.getLogger("tlspu.cookiepolicy")
UNINSTALL = "profile-tlspu.cookiepolicy:uninstall"


def uninstall(portal, reinstall=False):
    """ Uninstall this product.

        This external method is need, because portal_quickinstaller doens't
        know what GenericProfile profile to apply when uninstalling a product.
    """
    setup_tool = getToolByName(portal, 'portal_setup')
    if not reinstall:
        setup_tool.runAllImportStepsFromProfile(UNINSTALL)
        return "Ran all uninstall steps."
