# -*- coding: utf-8 -*-

try:
    from plone.app.blob.migrations import migrate as migrateBlob
except ImportError:
    # without plone.app.blob should never be possible that someone called the "migrateBlob" function
    pass
from redturtle.smartlink.interfaces import ISmartLink

def migrateSmartLink(context):
    return migrateBlob(context, 'Link', 'ATLink').splitlines()

def isATLink(oldObject, **kwargs):
    """Test if the object is a simple ATLink (i.e: is not a Smart Link)"""
    return not ISmartLink.providedBy(oldObject)

def isSmartLink(oldObject, **kwargs):
    """Test if the object is a Smart Link"""
    return ISmartLink.providedBy(oldObject)

# helper to build custom blob migrators for the given type
# some code stolen from the migration of plone.app.blob
def makeMigrator(context, portal_type, meta_type):
    """ generate a migrator for the given at-based portal type """
    from Products.contentmigration.archetypes import InplaceATItemMigrator
    
    class ATLinkMigrator(InplaceATItemMigrator):
        src_portal_type = portal_type
        src_meta_type = meta_type
        dst_portal_type = portal_type
        dst_meta_type = meta_type

        def last_migrate_externalLink(self):
            if self.old.getRemoteUrl() and ISmartLink.providedBy(self.new):
                self.new.setExternalLink(self.old.getRemoteUrl())
                self.new.reindexObject()

    return ATLinkMigrator


def migrateLinkToSmartLink(context):
    from Products.contentmigration.walker import CustomQueryWalker
    migrator = makeMigrator(context, 'Link', 'ATLink')
    walker = CustomQueryWalker(context, migrator, callBefore=isATLink, use_savepoint=True)
    walker.go()
    return walker.getOutput().splitlines()


def migrateSmartLinkToLink(context):
    from Products.contentmigration.walker import CustomQueryWalker
    migrator = makeMigrator(context, 'Link', 'ATLink')
    walker = CustomQueryWalker(context, migrator, callBefore=isSmartLink, use_savepoint=True)
    walker.go()
    return walker.getOutput().splitlines()
