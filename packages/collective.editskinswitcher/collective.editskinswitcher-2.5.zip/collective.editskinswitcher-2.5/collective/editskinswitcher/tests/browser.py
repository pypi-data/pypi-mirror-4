from zope.interface import providedBy
from plone.app.layout.viewlets import ViewletBase


class ShowInterfaces(ViewletBase):

    def index(self):
        ifaces = providedBy(self.request)
        return '\n'.join([str(i) for i in ifaces])
