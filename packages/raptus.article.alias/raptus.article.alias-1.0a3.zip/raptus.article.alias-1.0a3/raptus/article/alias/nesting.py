from Products.CMFCore.utils import getToolByName

from raptus.article.nesting.articles import Articles as BaseArticles
from raptus.article.alias.base import ProviderMixin

class Articles(BaseArticles, ProviderMixin):

    def getArticles(self, **kwargs):
        catalog = getToolByName(self.context, 'portal_catalog')
        return self.convertAliasBrains(catalog(portal_type='Article', path={'query': '/'.join(self.context.getPhysicalPath()),
                                                                            'depth': 1}, sort_on='getObjPositionInParent', **kwargs))
