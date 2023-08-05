# -*- coding: utf-8 -*-

from Products.Archetypes.utils import shasattr


def fix_meta_type(self):
    """This external method is needed to fix problems that the 0.1.0 version of the SmartLink lead.
    The bug is visible only on reordering... for some reason the _objects structure of every folder
    store the tuple (id, meta_type) but version 0.1.0 has a wrong meta type in the class.
    Effects: you can't order your folders if a SmartLink is inside!

    This method load all objects of your portal looking for the meta_type value as 'Link', and change
    those to 'ATLink'.
    """
    def _recurseFixMetaType(obj):
        cnt = 0
        if shasattr(obj, '_objects'):
            objects = obj._objects
            for o in objects:
                if o['meta_type'] == 'Link':
                    o['meta_type'] = 'ATLink'
                    print "Fixed object %s, subobject id is %s" % (obj.absolute_url_path(), o['id'])
                    cnt += 1
            obj._objects = objects
            subobjects = obj.objectValues()
            for o in subobjects:
                cnt += _recurseFixMetaType(o)
        return cnt

    portal = self.portal_url.getPortalObject()
    cnt = _recurseFixMetaType(portal)
    msgp = ""
    if cnt:
        msgp = "; reindex the catalog now!"
    return ("%s content modified" + msgp) % str(cnt)
