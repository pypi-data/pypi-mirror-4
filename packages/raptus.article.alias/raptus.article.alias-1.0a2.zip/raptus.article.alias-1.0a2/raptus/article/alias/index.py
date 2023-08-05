from zope.interface import implements
from zope.component import adapts

from plone.indexer.interfaces import IIndexer
from Products.ZCatalog.interfaces import IZCatalog

from raptus.article.alias.interfaces import IAlias

class Index(object):
    implements(IIndexer)
    adapts(IAlias, IZCatalog)
    def __init__(self, obj, catalog):
        self.obj = obj
    def __call__(self):
        return self.obj.Schema()['components'].get(self.obj)

class PortalType(object):
    implements(IIndexer)
    adapts(IAlias, IZCatalog)
    def __init__(self, obj, catalog):
        self.obj = obj
    def __call__(self):
        ref = self.obj.getReference()
        return self.obj.getReference().portal_type if ref is not None else None

class RefUID(object):
    implements(IIndexer)
    adapts(IAlias, IZCatalog)
    def __init__(self, obj, catalog):
        self.obj = obj
    def __call__(self):
        ref = self.obj.getReference()
        return self.obj.getReference().UID() if ref is not None else None
