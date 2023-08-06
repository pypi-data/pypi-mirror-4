from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Acquisition import aq_base, aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets import ViewletBase
from zope.component import getMultiAdapter
import time
import string
from zope.interface import implements
from Acquisition import aq_inner
from zope.component import getUtility
from Products.CMFPlone.interfaces import IPloneSiteRoot

class FooterView (BrowserView):
    """
    Footer menu. Reads the /footer page and generates a footer menu.
    A link to login_form will generate the default login menu with dropdown menu
    """
    implements(IViewlet)
    render = ViewPageTemplateFile('footer.pt')

    def __init__(self, context, request, view, manager):
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager
        
    def getFooterObject(self):
        urltool = getToolByName(self.context, 'portal_url')
        languagetool = getToolByName(self.context, 'portal_languages')
        portal = urltool.getPortalObject()
        try:
            lang = self.context.getLanguage()
        except:
            lang = languagetool.getDefaultLanguage()
            
        if lang == '':
            lang = "es"
            
        if hasattr(portal, lang):	 
	    if hasattr(portal[lang], "footer"):
	       return portal[lang].footer
	    else:
		return None
	else:
	    if hasattr(portal, "footer"):
	       return portal.footer
	    else:
		return None
        
    def generateFooter(self):
        footer = self.getFooterObject()
        if footer is not None:
            body = footer.getText()
            return body
        else:
            return ""
        
        
class GlobalSectionsViewlet(ViewletBase):
    index = ViewPageTemplateFile('sections.pt')

    def update(self):
        context = aq_inner(self.context)
        portal_tabs_view = getMultiAdapter((context, self.request),
                                           name='portal_tabs_view')
        self.portal_tabs = portal_tabs_view.topLevelTabs()

        self.selected_tabs = self.selectedTabs(portal_tabs=self.portal_tabs)
        self.selected_portal_tab = self.selected_tabs['portal']

    def getSubItems(self, tab):
	'''Get items for submenu
	'''
	tabPath = tab['url']
	#portal = self.context.restrictedTraverse("@@plone_portal_state").portal
	path = tabPath.split("/")
	queryPath = "/" + "/".join(path[-3:])
	catalog = getToolByName(self, 'portal_catalog')
	portal_workflow = getToolByName(self, 'portal_workflow')
	results = catalog.searchResults(path = {'query' : queryPath, 'depth' : 1 }, sort_on='getObjPositionInParent')
	
	subitems = []
	for item in results:
	    obj = item.getObject()
	    if not obj.exclude_from_nav() and portal_workflow.getInfoFor(obj, 'review_state') == 'published' or not getToolByName(self,'portal_membership').isAnonymousUser():
		subitems.append(obj)
		
	return subitems
	

    def selectedTabs(self, default_tab='index_html', portal_tabs=()):
        plone_url = getToolByName(self.context, 'portal_url')()
        plone_url_len = len(plone_url)
        request = self.request
        valid_actions = []

        url = request['URL']
        path = url[plone_url_len:]

        for action in portal_tabs:
            if not action['url'].startswith(plone_url):
                # In this case the action url is an external link. Then, we
                # avoid issues (bad portal_tab selection) continuing with next
                # action.
                continue
            action_path = action['url'][plone_url_len:]
            if not action_path.startswith('/'):
                action_path = '/' + action_path
            if path.startswith(action_path):
                # Make a list of the action ids, along with the path length
                # for choosing the longest (most relevant) path.
                valid_actions.append((len(action_path), action['id']))

        # Sort by path length, the longest matching path wins
        valid_actions.sort()
        if valid_actions:
            return {'portal' : valid_actions[-1][1]}

        return {'portal' : default_tab}
