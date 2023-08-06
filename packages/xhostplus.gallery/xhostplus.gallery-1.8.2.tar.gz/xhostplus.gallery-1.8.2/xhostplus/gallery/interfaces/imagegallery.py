from zope import schema
from zope.interface import Interface

try:
    # Plone >= 4.1
    from zope.container.constraints import contains
    from zope.container.constraints import containers
except ImportError:
    # Legacy Plone
    from zope.app.container.constraints import contains
    from zope.app.container.constraints import containers

from xhostplus.gallery import galleryMessageFactory as _

class IImageGallery(Interface):
    """An image gallery folder"""
    
    # -*- schema definition goes here -*-
