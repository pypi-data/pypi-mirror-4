from raptus.article.flash.adapters import Flashs as BaseFlashs
from raptus.article.alias.base import ProviderMixin

class Flashs(BaseFlashs, ProviderMixin):

    def getFlashs(self, **kwargs):
        return self.convertAliasBrains(super(Flashs, self).getFlashs(**kwargs))
