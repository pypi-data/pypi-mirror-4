from raptus.article.collections.collections import Collections as BaseCollections
from raptus.article.alias.base import ProviderMixin

class Collections(BaseCollections, ProviderMixin):

    def getCollections(self, **kwargs):
        return self.convertAliasBrains(super(Collections, self).getCollections(**kwargs))
