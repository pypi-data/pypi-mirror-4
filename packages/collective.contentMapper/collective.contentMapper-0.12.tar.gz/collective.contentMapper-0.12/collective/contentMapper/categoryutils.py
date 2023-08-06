from zope.component import getMultiAdapter
from zope.component import getUtility
from Products.CMFCore.utils import getToolByName
from plone.registry.interfaces import IRegistry
from collective.contentMapper.interfaces import ICoordinatesList
from Products.CMFPlone.interfaces import IPloneSiteRoot
try:
    from collective.virtualtreecategories.interfaces import IVirtualTreeCategoryConfiguration
    VTC_EXISTS = True
except ImportException:
    VTC_EXISTS = False

class CategoryUtils:
    ''' Usefull methods to deal with keywords with or without collective.virtualtreecategories '''
    
    def tools(self):
        """ returns tools view. Available items are all portal_xxxxx"""
        return getMultiAdapter((self.context, self.request), name=u"plone_tools")
        
    def catalog(self):
        return getToolByName(self.context, 'portal_catalog') 
    
    def getSiteCategoriesAsList(self):
        '''Get all the categories from the plone site'''
        vals = list(self.catalog().uniqueValuesFor('Subject'))
        vals.sort()
        return vals
    
    def vtcExists(self):
        return VTC_EXISTS
    
    def getVTCategories(self, path):
        if VTC_EXISTS:
            storage = IVirtualTreeCategoryConfiguration(getUtility(IPloneSiteRoot))
            return storage.list_categories(path)
        else:
            return None
        
    def getVTKeywords(self, path):
        if VTC_EXISTS:
            storage = IVirtualTreeCategoryConfiguration(getUtility(IPloneSiteRoot))
            return storage.list_keywords(path)
        else:
            return None
        
    def getAllKeywordsBelow(self, path):
        results = []
        subCats = self.getVTCategories(path)
        keywords = self.getVTKeywords(path)
        
        if keywords is not None:
            results.extend(keywords)
        
        if subCats is not None:
            for cat in subCats:
                results.extend(self.getAllKeywordsBelow(path + "/" + cat.id))
            
        return results
                

    def howManyResults(self, keyword):
        search = self.getResultsForCategoryList([keyword,])
        #print("found %s results for %s"%(len(search), keyword))
        return len(search)

    def cacheResults(self, keyword):
        res = self.howManyResults(keyword)
        
        registry = getUtility(IRegistry)
        list = registry.forInterface(ICoordinatesList)
        
        newList = []
        
        for location in list.locations:
            values = location.split(",")
            if values[0] == keyword:
                location = "%s,%s,%s,%s"%(values[0], values[1], values[2], res)
                print "updated from %s to %s"%(values[3], res)
                newList.append(location)
            else:
                if len(values) == 4:
                    location = "%s,%s,%s,%s"%(values[0], values[1], values[2], values[3])
                else:
                    location = "%s,%s,%s,0"%(values[0], values[1], values[2])
                newList.append(location)
        
        list.locations = newList
        
        return res
    
    
    def getResultsForCategoryList(self, categories):
        '''Malkes the search for all the items that have all the categories'''
        #print("Getting results from the wrong place")
        catalog = self.catalog()
        
        folder_path = '/'.join(self.context.getPhysicalPath())
        
        if self.context.portal_type == 'Topic':
            query = self.context.buildQuery()
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
    
    
    def generateQueryString(self, categories, adding=None, subtracting=None):
        '''Generates a URL querystring from a list of categories'''
        query = "?"
        finalCategories = list()
        
        if categories is not None:
            finalCategories = categories[:]
        
        if adding is not None:
            finalCategories.append(adding)
            
        if subtracting is not None:
            if subtracting in finalCategories:
                finalCategories.remove(subtracting)
        
        for cat in finalCategories:
            query = query + "Subject%3Alist=" + cat + "&"
        
        return query[:-1]