from random import sample

from zope.interface import Interface
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider

from zope import schema
from zope.formlib import form
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

try:
    from zope.schema.interfaces import IVocabularyFactory
except:
    from zope.app.schema.vocabulary import IVocabularyFactory

from xhostplus.gallery import galleryMessageFactory as _

class IGalleryPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    path = schema.Choice(title=_(u'Gallery path'),
                       description=_(u'The path to the gallery.'),
                       required=True,
                       vocabulary='xhostplus.gallery.GalleryVocabulary')

    count = schema.Int(title=_(u'Number of images'),
                       description=_(u'How many images to list.'),
                       required=True,
                       default=5)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IGalleryPortlet)

    def __init__(self, path='/', count=5):
        self.count = count
        self.path = path

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Gallery Portlet"

    def getGallery(self, context):
        """Returns the selected gallery object
        """
        catalog = getToolByName(context, 'portal_catalog') # getting the catalog for searching objects
        result = catalog(portal_type='Image Gallery',
                         path={
                             'query': self.path,
                             'depth': 0,
                         })

        if len(result) == 1:
            return result[0].getObject()
        return None

    def getImages(self, context):
        """Returns the selected gallery object
        """
        catalog = getToolByName(context, 'portal_catalog') # getting the catalog for searching objects
        results = catalog(portal_type='Image',
                         path={
                             'query': self.path,
                             'depth': 1,
                         })

        count = self.count
        if count > len(results):
            count = len(results)

        return sample([result.getObject() for result in results], count)

class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('galleryportlet.pt')

    @property
    def available(self):
        return self.gallery() and len(self.images()) > 0

    def gallery(self):
        return self.data.getGallery(self.context)

    def images(self):
        return self.data.getImages(self.context)

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IGalleryPortlet)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IGalleryPortlet)

class GalleryVocabulary(object):
    """ Ad Unit sizes """

    implements(IVocabularyFactory)

    def __call__(self, context):
        catalog = getToolByName(context, 'portal_catalog') # getting the catalog for searching objects
        results = catalog(portal_type='Image Gallery')
        found = []

        for result in results:
            found.append(SimpleTerm(result.getPath(), result.getPath(), result.getPath()))

        return SimpleVocabulary(found)


GalleryVocabularyFactory = GalleryVocabulary()
