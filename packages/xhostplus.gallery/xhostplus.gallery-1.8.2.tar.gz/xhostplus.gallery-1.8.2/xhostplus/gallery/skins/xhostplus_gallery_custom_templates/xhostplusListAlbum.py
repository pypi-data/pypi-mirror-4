## Script (Python) "xhostplusListAlbum"
##title=Helper method for xhostplus gallery view
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=images=0, folders=0, subimages=0

from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import getToolByName

result = {}

if images:
    result['images'] = context.getFolderContents({
        'portal_type': ('Image',)
    }, full_objects=True)

    if context.getShow_images_from_main_lang():
        ltool = getToolByName(context, 'portal_languages')
        preflang = ltool.getPreferredLanguage()
        deflang = ltool.getDefaultLanguage()

        if preflang != deflang and hasattr(context, 'getTranslation'):
            deflangcontext = context.getTranslation(deflang)
            deflangcontent = deflangcontext.getFolderContents({
                'portal_type': ('Image',),
                'Language' : (deflang, '', None),
            }, full_objects=True)
            result['images'] = result['images'] + deflangcontent
if folders:
    # We don't need the full objects for the folders
    result['folders'] = context.getFolderContents({
        'portal_type':('Image Gallery',)
    })
if subimages:
    #Handle brains or objects
    if base_hasattr(context, 'getPath'):
        path = context.getPath()
    else:
        path = '/'.join(context.getPhysicalPath())
    # Explicitly set path to remove default depth
    result['subimages'] = context.getFolderContents({
        'Type':('Image',),
        'path':path
    })

return result
