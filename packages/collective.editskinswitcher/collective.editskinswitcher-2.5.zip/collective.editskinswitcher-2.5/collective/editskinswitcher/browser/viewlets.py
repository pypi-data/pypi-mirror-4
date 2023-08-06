from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.instance import memoize


class PreviewViewlet(ViewletBase):
    """IFrame view on the default skin.

    This helps to preserve some WYSIWYG feel to the edit interface.
    """
    render = ViewPageTemplateFile("templates/preview_viewlet.pt")

    @memoize
    def objectURL(self):
        context = self.context
        return context.absolute_url() + '/view?mutate_skin=default'
