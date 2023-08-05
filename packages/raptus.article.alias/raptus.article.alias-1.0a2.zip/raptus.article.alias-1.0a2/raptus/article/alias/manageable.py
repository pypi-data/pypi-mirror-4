from OFS.interfaces import IOrderedContainer
from zope import interface, component

from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.CatalogTool import getObjPositionInParent

from raptus.article.core.manageable import Manageable as BaseManageable

class Manageable(BaseManageable):

    def getList(self, brains, component=''):
        items = []
        i = 0
        l = len(brains)
        pos = [getObjPositionInParent(brain.alias.getObject())() if getattr(brain, 'alias', None) is not None else getObjPositionInParent(brain.getObject())() for brain in brains]
        for brain in brains:
            obj = brain.getObject()
            if getattr(brain, 'alias', None) is not None:
                url = brain.alias.getURL()
                uid = brain.alias.UID
                id = brain.alias.id
                aobj = brain.alias.getObject()
            else:
                url = brain.getURL()
                uid = brain.UID
                id = brain.id
                aobj = obj
            try:
                components = aobj.Schema()['components'].get(aobj)
            except:
                components = []
            modify = self.mship.checkPermission(permissions.ModifyPortalContent, aobj)
            item = {'obj': obj,
                    'brain': brain,
                    'id': id,
                    'anchor': '%s%s' % (component, id),
                    'up': self.sort and i > 0 and self.sort_url % ('%s%s' % (component, id), pos[(i-1)] - pos[i], id) or None,
                    'down': self.sort and i < l - 1 and self.sort_url % ('%s%s' % (component, id), pos[(i+1)] - pos[i], id) or None,
                    'view': '%s/view' % url,
                    'edit': modify and '%s/edit' % url or None,
                    'delete': self.delete and self.mship.checkPermission(permissions.DeleteObjects, aobj) and '%s/delete_confirmation' % url or None,
                    'show': modify and component and not component in components and self.show_hide_url % ('%s%s' % (component, id), 'show', uid, component) or None,
                    'hide': modify and component and component in components and self.show_hide_url % ('%s%s' % (component, id), 'hide', uid, component) or None}
            items.append(item)
            i += 1
        return items
