from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from xhostplus.gallery import galleryMessageFactory as _


class IGalleryView(Interface):
    """
    Gallery view interface
    """


class GalleryView(BrowserView):
    """
    Gallery browser view
    """
    implements(IGalleryView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()
