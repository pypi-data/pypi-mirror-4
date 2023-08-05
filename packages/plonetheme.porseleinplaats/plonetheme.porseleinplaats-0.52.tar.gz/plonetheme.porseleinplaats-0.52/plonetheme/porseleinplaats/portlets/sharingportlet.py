import random

from AccessControl import getSecurityManager

from zope.interface import implements
from zope.component import getMultiAdapter, getUtility

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form

from plone.memoize.instance import memoize

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget

from plone.i18n.normalizer.interfaces import IIDNormalizer

from plone.portlet.collection import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName


class ISharingPortlet(IPortletDataProvider):
    """A portlet which renders the sharing buttons of the current object
    """


class Assignment(base.Assignment):
    """
    Portlet assignment.
    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(ISharingPortlet)

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen. Here, we use the title that the user gave.
        """
        return "Sharing Portlet"


class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('sharingportlet.pt')
    render = _template

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    @property
    def available(self):
        if self.context.portal_type == "Object":
            return True
        else:
            return False
        
    def getMedia(self, item, scale="large"):
	""" finds and returns relevant leading media for the context item
	"""
	if item.portal_type == 'Image':
	    return item.absolute_url() + '/image_%s'%scale
	
	catalog = getToolByName(self.context, 'portal_catalog')
	plone_utils = getToolByName(self.context, 'plone_utils')
	path = '/'.join(item.getPhysicalPath())
	
	if plone_utils.isStructuralFolder(item):
	    results = catalog.searchResults(path = {'query' : path,'depth' : 1 }, type = ['Image'], sort_on = 'getObjPositionInParent')
	    if len(results) > 0:
		leadMedia = results[0]
		if leadMedia.portal_type == 'Image':
		    return leadMedia.getURL() + '/image_%s'%scale
		else:
		    return None
	    else:
		return None
	else:
	    #TODO: Add lead image support and News Item Image support
	    return None
    
    def css_class(self):
        return "portlet-sharing"


class AddForm(base.NullAddForm):
     """Portlet add form.
     """
     def create(self):
         return Assignment()
