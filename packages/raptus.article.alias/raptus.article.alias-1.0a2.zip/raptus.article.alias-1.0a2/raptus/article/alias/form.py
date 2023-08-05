from raptus.article.form.forms import Forms as BaseForms
from raptus.article.alias.base import ProviderMixin

class Forms(BaseForms, ProviderMixin):

    def getForms(self, **kwargs):
        return self.convertAliasBrains(super(Forms, self).getForms(**kwargs))
