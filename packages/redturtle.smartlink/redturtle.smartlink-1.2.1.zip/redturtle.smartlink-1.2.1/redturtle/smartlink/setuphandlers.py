# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName

from redturtle.smartlink import logger
from redturtle.smartlink import smartlinkMessageFactory as _

PROFILE_ID = 'profile-redturtle.smartlink:default'

def atLinkToSmartLink(context):
    portal = context.getSite()

    if context.readDataFile('redturtle.smartlink_linkToSmartLink.txt') is None:
        return
    
    try:
        from redturtle.smartlink.migrator import migrateLinkToSmartLink
        logger.info("Starting migration of ATLink to Smart Link")
        messages = migrateLinkToSmartLink(portal)
        i = 0
        for m in messages:
            i+=1
            logger.info(m)
            portal.plone_utils.addPortalMessage(m, type="warning")
        portal.plone_utils.addPortalMessage(_('sequence_help_message',
                                              default=u"$num element(s) migrated",
                                              mapping={'num': i}))
        logger.info("Done")

    except ImportError:
        logger.error("Can't do anything. Check if Products.contentmigration is installed")


def smartLinkToATLink(context):
    """Run this to recover original Plone ATLink"""
    portal = context.getSite()

    if context.readDataFile('redturtle.smartlink_smartLinkToATLink.txt') is None:
        return
    
    try:
        from redturtle.smartlink.migrator import migrateSmartLinkToLink
        logger.info("Starting migration of Smart Link back to ATLink")
        messages = migrateSmartLinkToLink(portal)
        i = 0
        for m in messages:
            i+=1
            logger.info(m)
            portal.plone_utils.addPortalMessage(m, type="warning")
        portal.plone_utils.addPortalMessage(_('sequence_help_message',
                                              default=u"$num element(s) migrated",
                                              mapping={'num': i}))
        logger.info("Done")

    except ImportError:
        logger.error("Can't do anything. Check if Products.contentmigration is installed")


def migrateTo1002(context):
    setup_tool = getToolByName(context, 'portal_setup')
    setup_tool.runImportStepFromProfile(PROFILE_ID, 'rolemap')
    setup_tool.runImportStepFromProfile(PROFILE_ID, 'controlpanel')
    setup_tool.runImportStepFromProfile(PROFILE_ID, 'action-icons')
    logger.info("Migrated to 1.1.0")

def migrateTo1003(context):
    setup_tool = getToolByName(context, 'portal_setup')
    if setup_tool.getBaselineContextID() == 'profile-redturtle.smartlink:default' or \
            setup_tool.getBaselineContextID() == 'profile-redturtle.smartlink:uninstall':
        setup_tool.setBaselineContext('profile-Products.CMFPlone:plone')
        logger.info("Restoring the proper base line context for Generic Setup")
    logger.info("Migrated to 1.1.3")

def migrateTo1210(context):
    _REMOVE_IMPORT_STEPS = [
        'imaged-event',
    ]
    registry = context.getImportStepRegistry()
    remove = _REMOVE_IMPORT_STEPS
    for step in remove:
        if step in registry._registered:
            registry.unregisterStep(step)
            logger.info("Removing import_step %s" % step)
    logger.info("Migrated to 1.2.1")
