from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView
from zope.interface import implements
from collective.editskinswitcher.browser.interfaces import IPreviewView


class Preview(BrowserView):
    """IFrame view on the default skin.

    This preserve some WYSIWYG feel to the edit interface.
    """
    implements(IPreviewView)
    template = ViewPageTemplateFile('templates/preview_view.pt')

    def __call__(self):
        context = self.context
        self.objectURL = context.absolute_url()
        self.objectURL += '/view?mutate_skin=default'
        return self.template()
