from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from raptus.article.core import RaptusArticleMessageFactory as _

class View(BrowserView):
    """Alias view
    """
    template = ViewPageTemplateFile('view.pt')

    def __call__(self):
        return self.template()
