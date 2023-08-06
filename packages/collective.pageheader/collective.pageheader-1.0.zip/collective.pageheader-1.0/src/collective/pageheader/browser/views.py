# -*- coding: utf-8 -*-

from Acquisition import aq_inner
from Acquisition import aq_parent

from Products.Five import BrowserView
from Products.CMFPlone.interfaces import IPloneSiteRoot

# from plone.memoize.view import memoize as memoize_view
# from plone.memoize.view import memoize_contextless
from plone.memoize.instance import memoize as memoize_instance

from collective.pageheader.interfaces import IPageHeaderEnabled
from collective.pageheader.utils import get_pageheader_image
from collective.pageheader.extenders import PAGEHEADER_FIELDNAME


def get_parent(context):
    return aq_parent(aq_inner(context))


def is_plone_site(context):
    return IPloneSiteRoot.providedBy(context)


class PageHeaderView(BrowserView):
    """
    """

    def get_header(self, context=None, check_parent=True, tag=False, **kwargs):
        if context is None:
            context = self.context
        if is_plone_site(context):
            # go away immediately
            return None
        enabled = IPageHeaderEnabled.providedBy(context)
        header = enabled and get_pageheader_image(context)
        if header is None and check_parent:
            while not is_plone_site(context) and header is None:
                context = get_parent(context)
                header = self.get_header(context=context)
        if header and tag:
            scale_kargs = {'scale': 'large'}
            scale_kargs.update(kwargs)
            scales = context.restrictedTraverse('@@images')
            return scales.scale(PAGEHEADER_FIELDNAME, **scale_kargs)
        return header

    @memoize_instance
    def get_header_image(self):
        return self.get_header(context=self.context, tag=1)
