from raptus.article.table.adapters import Tables as BaseTables
from raptus.article.alias.base import ProviderMixin

class Tables(BaseTables, ProviderMixin):

    def getTables(self, **kwargs):
        return self.convertAliasBrains(super(Tables, self).getTables(**kwargs))
