from collective.contentMapper.categoryutils import CategoryUtils
from Products.CMFCore.utils import getToolByName

def objectAdded(object, event):
    try:
        subjects = object.Subject()
        util = CategoryUtils()
        urltool = getToolByName(context, "portal_url")
        portal = urltool.getPortalObject()
        util.context = portal
        
        if len(subjects) == 0:
            return
        else:
            for subject in subjects:
                print("Updating: %s"%subject)
                util.cacheResults(subject)
    except:
        raise