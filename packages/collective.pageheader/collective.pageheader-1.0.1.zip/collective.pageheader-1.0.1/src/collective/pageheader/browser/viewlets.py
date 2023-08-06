from plone.app.layout.viewlets import common
from zope.component import getMultiAdapter


class PageHeaderViewlet(common.ViewletBase):
    """
    """

    def available(self):
        return bool(self.get_header_image())

    @property
    def pageheader_view(self):
        return getMultiAdapter((self.context, self.request), name="pageheader")

    def get_header_image(self):
        return self.pageheader_view.get_header_image()
