from raptus.article.media.adapters import Audios as BaseAudios, Videos as BaseVideos
from raptus.article.alias.base import ProviderMixin

class Audios(BaseAudios, ProviderMixin):

    def getAudios(self, **kwargs):
        return self.convertAliasBrains(super(Audios, self).getAudios(**kwargs))

class Videos(BaseVideos, ProviderMixin):

    def getVideos(self, **kwargs):
        return self.convertAliasBrains(super(Videos, self).getVideos(**kwargs))
