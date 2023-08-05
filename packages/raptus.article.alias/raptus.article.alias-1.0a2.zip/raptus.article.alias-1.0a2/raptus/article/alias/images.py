from raptus.article.images.images import Images as BaseImages
from raptus.article.alias.base import ProviderMixin

class Images(BaseImages, ProviderMixin):

    def getImages(self, **kwargs):
        return self.convertAliasBrains(super(Images, self).getImages(**kwargs))
