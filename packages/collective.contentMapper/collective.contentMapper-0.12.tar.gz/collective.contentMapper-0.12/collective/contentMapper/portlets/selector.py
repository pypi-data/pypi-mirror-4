from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from collective.contentMapper.categoryutils import CategoryUtils
from collective.contentMapper.interfaces import ICoordinatesList
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

from collective.contentMapper import contentMapperMessageFactory as _

class IMapNavigatorPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """
    visualTitle = schema.TextLine(
        title=_(u"Title of the portlet"),
        description=_(u"The title that appears on top of the map'"),
        default=u'Locations',
        required=True
    )
    
    navigator = schema.TextLine(
        title=_(u"Send search to"),
        description=_(u"Which navigator should receive the search querys for this portlet. leave 'search' to use Plone search result page'"),
        default=u'search',
        required=True
    )
    
    rootCategory = schema.TextLine(
        title=_(u"Category"),
        description=_(u"Which virtual tree category root contains the region names to map"),
        default=u'',
        required=False
    )
    
    levels = schema.TextLine(
        title=_(u"Marker levels"),
        description=_(u"There are 3 sizes of markers. Choose the number of results at which the size increses. ex: '1,3,4' will have a small marker for 1 result medium marker for 2 or 3 results and a big marker for 4 or higher."),
        default=u'1,3,4',
        required=False
    )
    
    description = schema.TextLine(
        title=_(u"Description"),
        description=_(u"Description text to add to the portlet"),
        default=u'',
        required=False
    )
    
class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IMapNavigatorPortlet)

    def __init__(self, navigator=u'search', rootCategory=u'', visualTitle=u'Locations', levels=u'1,3,4', description=u''):
	self.navigator = navigator
	self.rootCategory = rootCategory
	self.visualTitle = visualTitle
	self.levels = levels
	self.description = description

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Map Navigator Portlet"


class Renderer(base.Renderer, CategoryUtils):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('mapNavigator.pt')
    
    @property
    def available(self):
        if len(self.getSiteCategoriesAsList()) == 0:
            return False
        else:
            return True
    
    @property
    def rootCategory(self):
	return self.data.rootCategory
    
    def Title(self):
	return self.data.visualTitle
    
    def Description(self):
	return self.data.description
    
    def getXPosition(self, region=None):
	if region is not None:
	    registry = getUtility(IRegistry)
	    list = registry.forInterface(ICoordinatesList)
	    for location in list.locations:
		values = location.split(",")
		if values[0] == region:
		    return int(values[1])
	    
	    return -1
	
    def getYPosition(self, region=None):
	if region is not None:
	    registry = getUtility(IRegistry)
	    list = registry.forInterface(ICoordinatesList)
	    for location in list.locations:
		values = location.split(",")
		if values[0] == region:
		    return int(values[2])
	    
	    return -1
	
    def getNumberOfResults(self, region=None):
	if region is not None:
	    registry = getUtility(IRegistry)
	    list = registry.forInterface(ICoordinatesList)
	    for location in list.locations:
		values = location.split(",")
		if values[0] == region:
		    return int(values[3])
	    
	    return 0
    
    def getResultsForCategoryList(self, categories):
        '''Malkes the search for all the items that have all the categories'''
	#print("GETTING RESULTS")
        catalog = self.catalog()
        
        #folder_path = '/'.join(self.context.getPhysicalPath())
	urltool = getToolByName(self, 'portal_url')
	portal = urltool.getPortalObject();
	splt = self.data.navigator.split("/")
	
	nav = portal
	
	for node in splt:
	    nav = nav[node]
	    
	folder_path = '/'.join(nav.getPhysicalPath())
	
        if nav.portal_type == 'Topic':
            query = nav.buildQuery()
	    if 'Subject' in query.keys():
                currentSubject = query['Subject']['query']
                for tag in currentSubject:
                    if tag not in categories:
                        categories.append(tag)
            query['Subject'] = {'query':categories, 'operator':'and'}
            results = catalog.searchResults(query)
        else:
            results = catalog.searchResults(path={'query': folder_path}, Subject={'query':categories, 'operator':'and'}, batch=True)
        return results
    
    def getMarkerImage(self, nr):
	levels = self.data.levels.split(",")
	if nr == 0:
	    return '0'
	
	image = "++resource++collective.contentMapper.images/SmallMarker.png"
	
	if nr >= int(levels[1]) and nr < int(levels[2]):
	    #medium
	    image = "++resource++collective.contentMapper.images/MediumMarker.png"
	elif nr >= int(levels[2]):
	    #big
	    image = "++resource++collective.contentMapper.images/BigMarker.png"
	
	return image
	
    
    def getPositionCSSFor(self, cat, markerImage):
	x = self.getXPosition(cat) 
	y = self.getYPosition(cat)
	z = 9999
	
	if x == -1 or y == -1:
	    return 'display:none'
	
	if markerImage == "++resource++collective.contentMapper.images/SmallMarker.png":
	    x=x-4
	    y=y-4
	    z=9999
	elif markerImage == "++resource++collective.contentMapper.images/MediumMarker.png":
	    x=x-14
	    y=y-14
	    z=9998
	elif markerImage == "++resource++collective.contentMapper.images/BigMarker.png":
	    x=x-35
	    y=y-35
	    z=9997
	    
	if x != -5:
	    return 'position:absolute; top:%spx; left:%spx; z-index:%s'%(y, x, z)
	    
    def getTooltipPositionCSS(self, markerImage):
	if markerImage == "++resource++collective.contentMapper.images/SmallMarker.png":
	    y=-30
	    x=10
	elif markerImage == "++resource++collective.contentMapper.images/MediumMarker.png":
	    y=-50
	    x=25
	elif markerImage == "++resource++collective.contentMapper.images/BigMarker.png":
	    y=-105
	    x=52
	    
	return 'position:absolute; top:%spx; left:%spx;'%(y, x)
    
	    
    def generateQueryString(self, categories, adding=None, subtracting=None):
        '''Generates a URL querystring from a list of categories'''
        query = "/" + self.data.navigator + "?"
        finalCategories = list()
        
        if categories is not None:
            finalCategories = categories[:]
        
        if adding is not None:
            finalCategories.append(adding)
            
        if subtracting is not None:
            if subtracting in finalCategories:
                finalCategories.remove(subtracting)
        
	if len(finalCategories) == 0:
	    #return self.context.absolute_url()
	    return ""
	
        for cat in finalCategories:
            query = query + "Subject%3Alist=" + cat + "&"
        
        return query[:-1]


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IMapNavigatorPortlet)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IMapNavigatorPortlet)
