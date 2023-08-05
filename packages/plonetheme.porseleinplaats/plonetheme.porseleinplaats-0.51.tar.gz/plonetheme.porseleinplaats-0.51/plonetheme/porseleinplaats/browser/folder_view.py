import time
import string
from Acquisition import aq_inner
from zope.component import getUtility
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from zope.security import checkPermission

try:
    from collective.flowplayer.interfaces import IFlowPlayable
    from collective.flowplayer.interfaces import IAudio
    FLOWPLAYER_EXISTS = True
except ImportError:
    FLOWPLAYER_EXISTS = False

try:
    from collective.contentleadimage.config import IMAGE_FIELD_NAME
    from collective.contentleadimage.leadimageprefs import ILeadImagePrefsForm
    LEADIMAGE_EXISTS = True
except ImportError:
    LEADIMAGE_EXISTS = False    


class FolderView(BrowserView):
    @property
    def prefs(self):
        portal = getUtility(IPloneSiteRoot)
        return ILeadImagePrefsForm(portal)

    def tag(self, obj, scale="thumb" ,css_class='tileImage'):
	if LEADIMAGE_EXISTS:
	    context = aq_inner(obj)
	    field = context.getField(IMAGE_FIELD_NAME)
	    if field is not None:
		if field.get_size(context) != 0:
		    return field.tag(context, scale=scale, css_class=css_class)
	    return ''
	else:
	    return ''

    def currenttime(self):
	return time.time()
    
    def trimDescription(self, desc, num):
	if len(desc) > num: 
		res = desc[0:num]
		lastspace = res.rfind(" ")
		res = res[0:lastspace] + " ..."
		return res
	else:
		return desc

    def toLocalizedTime(self, time, long_format=None, time_only = None):
        """Convert time to localized time
        """
        util = getToolByName(self.context, 'translation_service')
        try:
            return util.ulocalized_time(time, long_format, time_only, self.context,
                                        domain='plonelocales')
        except TypeError: # Plone 3.1 has no time_only argument
            return util.ulocalized_time(time, long_format, self.context,
                                        domain='plonelocales')

    def getFolderishContents(self, folder):
	catalog = getToolByName(self, 'portal_catalog')
	path = folder.getPath()
	if folder.portal_type == "Folder":
		results = catalog.searchResults(path = {'query' : path,'depth' : 1 }, sort_on = 'getObjPositionInParent')[:3]
	elif folder.portal_type == "Topic":
		query = folder.getObject().buildQuery()
		if query != None:
			results = catalog.searchResults(query)[:3]
		else:
			results = []
	else:
		results = []

	return results
	
    def canModifyContent(self, item=None):
	if item is None:
	    return checkPermission('cmf.ModifyPortalContent', self.context)
	else:
	    return checkPermission('cmf.ModifyPortalContent', item)
	

    def translateMonth(self, month):
	if((self.request['LANGUAGE'])[:2] == 'en'):
	    return month
	elif ((self.request['LANGUAGE'])[:2] == 'es'):
	    if month == "Jan":
		return "Ene"
	    elif month == "Apr":
		return "Abr"
	    elif month == "Aug":
		return "Ago"
	    elif month == "Dec":
		return "Dic"
	    else:
		return month
	else:
	    return month
    
    def filterResults(self, results):
        '''Takes away Items of diferent languages than the current
        '''
        filtered = []
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        for item in results:
            if(portal_state.language() == item.Language):
                filtered.append(item)
        
        return filtered

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
		    return self.tag(item, scale=scale)
	    else:
		return self.tag(item, scale=scale)
	else:
	    return self.tag(item, scale=scale)
    
    def isVideo(self, item):
	if FLOWPLAYER_EXISTS:
	    result = IFlowPlayable.providedBy(item)
	    return result
	else:
	    return False

    def audio_only(self, item):
	if FLOWPLAYER_EXISTS:
	    result = IAudio.providedBy(item)
	    return result
	else:
	    return False
	