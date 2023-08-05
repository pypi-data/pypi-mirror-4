from raptus.article.links.links import Links as BaseLinks
from raptus.article.alias.base import ProviderMixin

class Links(BaseLinks, ProviderMixin):

    def getLinks(self, **kwargs):
        return self.convertAliasBrains(super(Links, self).getLinks(**kwargs))
