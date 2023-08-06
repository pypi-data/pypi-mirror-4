"""Main product initializer
"""
from Products.CMFPlone.utils import classImplements

from zope.i18nmessageid import MessageFactory
from collective.contentMapper import config

from Products.Archetypes import atapi
from Products.CMFCore import utils
#from Products.ATContentTypes.content.document import ATDocument
#from Products.ATContentTypes.content.newsitem import ATNewsItem
#from Products.ATContentTypes.content.file import ATFile
#from Products.ATContentTypes.content.event import ATEvent
#from Products.ATContentTypes.content.link import ATLink
#from Products.ATContentTypes.content.image import ATImage
#from collective.contentMapper.interfaces import MayHaveTagsWithCoordinates

# Define a message factory for when this product is internationalised.
# This will be imported with the special name "_" in most modules. Strings
# like _(u"message") will then be extracted by i18n tools for translation.

contentMapperMessageFactory = MessageFactory('collective.contentMapper')


def initialize(context):
    """Initializer called when used as a Zope 2 product.

    This is referenced from configure.zcml. Regstrations as a "Zope 2 product"
    is necessary for GenericSetup profiles to work, for example.

    Here, we call the Archetypes machinery to register our content types
    with Zope and the CMF.
    """
    
    #classImplements(ATDocument,MayHaveTagsWithCoordinates)
    #classImplements(ATNewsItem,MayHaveTagsWithCoordinates)
    #classImplements(ATFile,MayHaveTagsWithCoordinates)
    #classImplements(ATEvent,MayHaveTagsWithCoordinates)
    #classImplements(ATLink,MayHaveTagsWithCoordinates)
    #classImplements(ATImage,MayHaveTagsWithCoordinates)

    # Retrieve the content types that have been registered with Archetypes
    # This happens when the content type is imported and the registerType()
    # call in the content type's module is invoked. Actually, this happens
    # during ZCML processing, but we do it here again to be explicit. Of
    # course, even if we import the module several times, it is only run
    # once.

    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(config.PROJECTNAME),
        config.PROJECTNAME)

    # Now initialize all these content types. The initialization process takes
    # care of registering low-level Zope 2 factories, including the relevant
    # add-permission. These are listed in config.py. We use different
    # permissions for each content type to allow maximum flexibility of who
    # can add which content types, where. The roles are set up in rolemap.xml
    # in the GenericSetup profile.

    for atype, constructor in zip(content_types, constructors):
        utils.ContentInit('%s: %s' % (config.PROJECTNAME, atype.portal_type),
            content_types=(atype, ),
            permission=config.ADD_PERMISSIONS[atype.portal_type],
            extra_constructors=(constructor,),
            ).initialize(context)
