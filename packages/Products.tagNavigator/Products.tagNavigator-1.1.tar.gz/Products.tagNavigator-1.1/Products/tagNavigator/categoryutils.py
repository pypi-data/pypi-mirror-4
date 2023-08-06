from zope.component import getMultiAdapter
from zope.component import getUtility
from Products.CMFPlone.interfaces import IPloneSiteRoot
try:
    from collective.virtualtreecategories.interfaces import IVirtualTreeCategoryConfiguration
    VTC_EXISTS = True
except ImportException:
    VTC_EXISTS = False

class CategoryUtils:
    ''' Usefull methods to deal with categories with or without collective.virtualtreecategories '''
    
    def tools(self):
        """ returns tools view. Available items are all portal_xxxxx"""
        return getMultiAdapter((self.context, self.request), name=u"plone_tools")
    
    
    def getSiteCategoriesAsList(self):
        '''Get all the categories from the plone site'''
        vals = list(self.tools().catalog().uniqueValuesFor('Subject'))
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
    
    def getResultsForCategoryList(self, categories):
        '''Malkes the search for all the items that have all the categories'''
        catalog = self.tools().catalog()
        
        folder_path = '/'.join(self.context.getPhysicalPath())
        
        if self.context.portal_type == 'Topic':
            query = self.context.buildQuery()
            if 'Subject' in query.keys():
                #import pdb; pdb.set_trace()
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