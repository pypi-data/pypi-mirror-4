from zope.interface import Interface
from zope.interface import implements
from zope.component import adapts, getMultiAdapter

from plone.memoize.instance import memoize

from plone.app.portlets.portlets import navigation
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.interfaces import INavigationQueryBuilder
from plone.app.layout.navigation.root import getNavigationRoot
from plone.app.layout.navigation.navtree import buildFolderTree

from zope import schema
from zope.formlib import form
from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFPlone import utils

from collective.portlet.sitemap import NavigationExtendedPortletMessageFactory as _

class INavigationExtendedPortlet(navigation.INavigationPortlet) :
    """A portlet

    It inherits from INavigationPortlet
    """
    displayAsSiteMap = schema.Bool(
            title=_(u"label_display_as_site_map", default=u"Display as Site Map"),
            description=_(u"help_display_as_site_map",
                          default=u"If checked display all folders as a site map"),
            default=True,
            required=False)
            
    siteMapDepth = schema.Int(
            title=_(u"label_site_map_depth",
                    default=u"Site map depth"),
            description=_(u"help_site_map_depth",
                          default=u"If previous field is checked set the site map depth"),
            default=2,
            required=False)            

class Assignment(navigation.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(INavigationExtendedPortlet)
        
    title = _(u'Navigation Extended')
    
    name = u""
    root = None
    currentFolderOnly = False
    includeTop = False
    topLevel = 0
    bottomLevel = 0
    displayAsSiteMap = True
    siteMapDepth = 2
    
    
    def __init__(self, name=u"", root=None, currentFolderOnly=False, includeTop=False, topLevel=0, bottomLevel=0, displayAsSiteMap=True, siteMapDepth = 2):
        self.name = name
        self.root = root
        self.currentFolderOnly = currentFolderOnly
        self.includeTop = includeTop
        self.topLevel = topLevel
        self.bottomLevel = bottomLevel     
        self.displayAsSiteMap = displayAsSiteMap    
        self.siteMapDepth = siteMapDepth       



class Renderer(navigation.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    
    @memoize
    def getNavTree(self, _marker=[]):
        context = aq_inner(self.context)
        
        # Special case - if the root is supposed to be pruned, we need to
        # abort here

        queryBuilder = getMultiAdapter((context, self.data), INavigationExtendedQueryBuilder)
        strategy = getMultiAdapter((context, self.data), INavtreeStrategy)

        return buildFolderTree(context, obj=context, query=queryBuilder(), strategy=strategy)

    
    recurse = ViewPageTemplateFile('navigation_extended_recurse.pt')


class AddForm(navigation.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(INavigationExtendedPortlet)

    def create(self, data):
        return Assignment(name=data.get('name', u""),
                          root=data.get('root', u""),
                          currentFolderOnly=data.get('currentFolderOnly', False),
                          includeTop=data.get('includeTop', False),
                          topLevel=data.get('topLevel', 0),
                          bottomLevel=data.get('bottomLevel', 0),
                          displayAsSiteMap=data.get('displayAsSiteMap', True),
                          siteMapDepth=data.get('siteMapDepth', 2))



class EditForm(navigation.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(INavigationExtendedPortlet)
    

class INavigationExtendedQueryBuilder(INavigationQueryBuilder):
    """An object which returns a catalog query when called, used to 
    construct a navigation tree.
    """
    
    def __call__():
        """Returns a mapping describing a catalog query used to build a
           navigation structure.
        """    

class NavigationExtendedQueryBuilder(object):
    """Build a navtree query based on the settings in navtree_properties
    and those set on the portlet.
    """
    implements(INavigationExtendedQueryBuilder)
    adapts(Interface, INavigationExtendedPortlet)

    def __init__(self, context, portlet):
        self.context = context
        self.portlet = portlet
        
        portal_properties = utils.getToolByName(context, 'portal_properties')
        navtree_properties = getattr(portal_properties, 'navtree_properties')
        
        portal_url = utils.getToolByName(context, 'portal_url')
        
        # Acquire a custom nav query if available
        customQuery = getattr(context, 'getCustomNavQuery', None)
        if customQuery is not None and utils.safe_callable(customQuery):
            query = customQuery()
        else:
            query = {}

        # Construct the path query

        rootPath = getNavigationRoot(context, relativeRoot=portlet.root)
        currentPath = '/'.join(context.getPhysicalPath())

        # If we are above the navigation root, a navtree query would return
        # nothing (since we explicitly start from the root always). Hence,
        # use a regular depth-1 query in this case.

        if portlet.displayAsSiteMap :
                query['path'] = {'query' : rootPath, 'depth' : portlet.siteMapDepth}    
        else :
            if not currentPath.startswith(rootPath):
                query['path'] = {'query' : rootPath, 'depth' : 1}
            else:
                query['path'] = {'query' : currentPath, 'navtree' : 1}
                
        #print query        

        topLevel = portlet.topLevel or navtree_properties.getProperty('topLevel', 0)
        if topLevel and topLevel > 0:
             query['path']['navtree_start'] = topLevel + 1

        # XXX: It'd make sense to use 'depth' for bottomLevel, but it doesn't
        # seem to work with EPI.

        # Only list the applicable types
        query['portal_type'] = utils.typesToList(context)

        # Apply the desired sort
        sortAttribute = navtree_properties.getProperty('sortAttribute', None)
        if sortAttribute is not None:
            query['sort_on'] = sortAttribute
            sortOrder = navtree_properties.getProperty('sortOrder', None)
            if sortOrder is not None:
                query['sort_order'] = sortOrder

        # Filter on workflow states, if enabled
        if navtree_properties.getProperty('enable_wf_state_filtering', False):
            query['review_state'] = navtree_properties.getProperty('wf_states_to_show', ())

        self.query = query

    def __call__(self):
        return self.query




