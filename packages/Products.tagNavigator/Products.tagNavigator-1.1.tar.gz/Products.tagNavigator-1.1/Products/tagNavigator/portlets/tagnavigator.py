from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.tagNavigator.categoryutils import CategoryUtils

from Products.tagNavigator import tagNavigatorMessageFactory as _

class ITagNavigatorPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """
    portlet_title = schema.TextLine(
        title=_(u'Portlet title'),
        description=_(u'Title in portlet.'),
        required=False,
        default=u'Tag Navigator'
    )
    
    collapse = schema.Int(
        title=_(u"Levels to collapse"),
        description=_(u"First tree level number to collapse, 0 for no collapse, 1 or 2 for collapsing categories or subcategories"),
        default=0,
        required=False
    )
    
    #Accumulate?? - to be able to accumulate tags
    
    description = schema.TextLine(
        title=_(u"Description"),
        description=_(u"Text to show on top of the tag selector."),
        default=u'',
        required=False
    )
    
class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(ITagNavigatorPortlet)

    def __init__(self, portlet_title=u'Tag Navigator', collapse=0, description=u''):
	self.portlet_title = portlet_title
	self.collapse = collapse
	self.description = description

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Tag Navigator Portlet"


class Renderer(base.Renderer, CategoryUtils):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('tagnavigator.pt')
    
    @property
    def available(self):
        if len(self.getSiteCategoriesAsList()) == 0:
            return False
        else:
	    if self.context.portal_type=="Folder" or self.context.portal_type=="Topic":
		return True
	    else:
		return False
    
    @property
    def Description(self):
	return self.data.description
    
    @property
    def Portlet_title(self):
	return self.data.portlet_title
    
    @property
    def Collapse(self):
	return self.data.collapse
    
    def generateQueryString(self, categories, adding=None, subtracting=None):
        '''Generates a URL querystring from a list of categories'''
        if len(categories) <= 1  and subtracting is not None:
	    query = ""
	    return query
	else:
	    query = "/tagnavigator_view?"
	    
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


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(ITagNavigatorPortlet)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(ITagNavigatorPortlet)
