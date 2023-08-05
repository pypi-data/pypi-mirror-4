from raptus.article.files.files import Files as BaseFiles
from raptus.article.alias.base import ProviderMixin

class Files(BaseFiles, ProviderMixin):

    def getFiles(self, **kwargs):
        return self.convertAliasBrains(super(Files, self).getFiles(**kwargs))
