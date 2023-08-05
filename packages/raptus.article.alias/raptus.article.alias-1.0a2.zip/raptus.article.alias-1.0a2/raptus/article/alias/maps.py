from raptus.article.maps.adapters import Maps as BaseMaps
from raptus.article.alias.base import ProviderMixin

class Maps(BaseMaps, ProviderMixin):

    def getMaps(self, **kwargs):
        return self.convertAliasBrains(super(Maps, self).getMaps(**kwargs))
