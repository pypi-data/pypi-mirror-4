import logging

from Products.CMFCore.utils import getToolByName


def install(context):

    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.

    if context.readDataFile('tlspu.cookiepolicy_install.txt') is None:
        return

    # Add additional setup code here


def uninstall(context):
    """Uninstall code.

    Note that CMFQuickInstaller removes some stuff for us
    automatically, though it is good form to remove it ourselves.  And
    it does not undo everything.  Most things that it does not handle,
    can be handled in GenericSetup xml files with a remove='True'
    added, but this is not supported for all files.  In some files it
    even breaks.  We handle those cases here.
    """

    if context.readDataFile('tlspu.cookiepolicy_uninstall.txt') is None:
        return

    portal = context.getSite()
    logger = context.getLogger('tlspu.cookiepolicy')
    portal_conf = getToolByName(portal, 'portal_controlpanel')
    portal_conf.unregisterConfiglet('cookiepolicy')
    logger.info('Unregistered our cookiepolicy control panel configlet.')

    # Remove our properties from portal properties.
    pp = getToolByName(portal, 'portal_properties')
    if hasattr(pp, 'tlspu_cookiepolicy_properties'):
        pp.manage_delObjects(ids='tlspu_cookiepolicy_properties')
        logger.info('Removed tlspu_cookiepolicy_properties.')

    # We may still have persistent steps.  Remove them.
    remove_persistent_import_step(portal, logger=logger)


def remove_persistent_import_step(context, logger=None):
    """Import steps should not be persistent.

    Defining them in import_steps.xml makes them persistent and may
    break some Plone versions when you remove the product.

    Instead, they should be defined in zcml.

    Here we remove our old persistent import steps.
    """
    if logger is None:
        # Called as upgrade step: define our own logger.
        logger = logging.getLogger("tlspu.cookiepolicy")

    # context may be portal_setup or the site root.
    setup = getToolByName(context, 'portal_setup')
    # context is portal_setup which is nice
    registry = setup.getImportStepRegistry()
    old_steps = [u"tlspu.cookiepolicy.install",
                 u"tlspu.cookiepolicy.uninstall"]
    for old_step in old_steps:
        if old_step in registry.listSteps():
            try:
                registry.unregisterStep(old_step)
            except AttributeError:
                # BBB for GS 1.3
                del registry._registered[old_step]

            # Unfortunately we manually have to signal to portal_setup
            # that it has changed otherwise this change is not
            # persisted.
            setup._p_changed = True
            logger.info("Persistent %s import step removed from registry.",
                        old_step)
