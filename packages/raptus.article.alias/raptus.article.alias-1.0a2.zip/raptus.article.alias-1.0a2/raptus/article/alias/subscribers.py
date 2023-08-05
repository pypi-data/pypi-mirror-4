from zope.component import adapter
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from Products.Archetypes.interfaces import IReferenceable

@adapter(IReferenceable, IObjectModifiedEvent)
def reindexAliasesOnModified(object, event):
    for alias in object.getBackReferences('aliasTo'):
        alias.reindexObject()
