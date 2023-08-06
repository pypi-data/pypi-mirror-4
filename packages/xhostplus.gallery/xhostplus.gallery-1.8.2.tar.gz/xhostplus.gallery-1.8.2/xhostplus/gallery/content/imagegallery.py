"""Definition of the Image Gallery content type
"""

from zope.interface import implements, directlyProvides

try:
    from Products.LinguaPlone import public as atapi
except ImportError:
    # No multilingual support
    from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from xhostplus.gallery import galleryMessageFactory as _
from xhostplus.gallery.interfaces import IImageGallery
from xhostplus.gallery.config import PROJECTNAME

ImageGallerySchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.BooleanField('show_image_titles',
        languageIndependent=1,
        widget=atapi.BooleanWidget(
              label=_(u'Show image titles'),
              description=_(u"Whether the image titles should be shown or not."),
        ),
        required=False,
        searchable=False,
        default=True,
    ),

    atapi.BooleanField('slideshow',
        languageIndependent=1,
        widget=atapi.BooleanWidget(
              label=_(u'Enable slideshow'),
              description=_(u"Whether the slideshow is enabled or not."),
        ),
        required=False,
        searchable=False,
        default=False,
    ),

    atapi.IntegerField('slideshow_interval',
        languageIndependent=1,
        widget=atapi.IntegerWidget(
              label=_(u'Slideshow interval'),
              description=_(u"Seconds to wait for switching to the next image."),
        ),
        required=True,
        searchable=False,
        default=5,
    ),

    atapi.BooleanField('auto_exclude_from_nav',
        languageIndependent=1,
        widget=atapi.BooleanWidget(
              label=_(u'Exclude images from navigation'),
              description=_(u"Whether new images, uploaded via multi-upload, should be excluded from navigation."),
        ),
        required=False,
        searchable=False,
        default=True,
    ),

    atapi.IntegerField('page_size',
        languageIndependent=1,
        widget=atapi.IntegerWidget(
              label=_(u'Page size'),
              description=_(u"The number of images on one page. Enter 0 to show all images on one page."),
        ),
        required=True,
        searchable=False,
        default=12,
    ),

    atapi.BooleanField('show_images_from_main_lang',
        languageIndependent=1,
        widget=atapi.BooleanWidget(
              label=_(u'Images from main language'),
              description=_(u"Show galleries images of the main language in all translations."),
        ),
        required=False,
        searchable=False,
        default=False,
    ),

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

ImageGallerySchema['title'].storage = atapi.AnnotationStorage()
ImageGallerySchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    ImageGallerySchema,
    folderish=True,
    moveDiscussion=False
)

class ImageGallery(folder.ATFolder):
    """An image gallery folder"""
    implements(IImageGallery)

    meta_type = "Image Gallery"
    schema = ImageGallerySchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

    def effective_page_size(self, images):
        """If the page size is lower equal 0, all images should be shown on
        one page. This method returns the number of images in that case.
        """
        page_size = self.getPage_size()

        if page_size <= 0:
            return len(images)
        return page_size

    def validate_slideshow_interval(self, value):
        try:
            value = int(value)
        except ValueError:
            return _(u"The interval time should be an integer.")
        if value < 1:
            return _(u"The interval time should not be lower than 1.")
        if value > 30:
            return _(u"The interval time should not be greater than 30.")
        return None

atapi.registerType(ImageGallery, PROJECTNAME)
