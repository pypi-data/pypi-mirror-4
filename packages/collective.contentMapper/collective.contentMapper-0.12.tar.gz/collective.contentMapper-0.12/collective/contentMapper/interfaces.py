from z3c.form import interfaces
from zope.interface import Interface
from zope import schema

class ICoordinatesList(Interface):
    """ A Record to keep the list of strings that match a region name to a x,y coordinate """
    locations = schema.List(title=u"List of regions / locations",
                            description=u"List of strings in the format name,x,y that maps region names to x y values on the map image",
                            default = [ ],
                            required=True,
                            missing_value=[ ],
                            value_type=schema.TextLine(title=u"Region", default=u'None'))
    
    
class MayHaveTagsWithCoordinates(Interface):
    """ This object wants to export its titles to Type X """
