import time
import string
from Acquisition import aq_inner
from zope.component import getUtility
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.interfaces import IPloneSiteRoot
from collective.contentleadimage.config import IMAGE_FIELD_NAME
from collective.contentleadimage.leadimageprefs import ILeadImagePrefsForm
from zope.component import getMultiAdapter
from collective.flowplayer.interfaces import IFlowPlayable
from collective.flowplayer.interfaces import IAudio
from Products.CMFCore.utils import getToolByName

class ObjectView(BrowserView):
    
    @property
    def prefs(self):
        portal = getUtility(IPloneSiteRoot)
        return ILeadImagePrefsForm(portal)

    def tag(self, obj, css_class='tileImage'):
        context = aq_inner(obj)
        field = context.getField(IMAGE_FIELD_NAME)
        if field is not None:
            if field.get_size(context) != 0:
                scale = self.prefs.desc_scale_name
                return field.tag(context, scale=scale, css_class=css_class)
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

    def getTileMedia(self, item):
	catalog = getToolByName(self, 'portal_catalog')
	try:
	    path = item.getPath()
	except:
	    path = "/".join(item.getPhysicalPath())

	if item.portal_type == "MediaPage" or item.portal_type == "Object" :
	    results = catalog.searchResults(path = {'query' : path,'depth' : 1 }, type = 'Image', sort_on = 'getObjPositionInParent')
	    if len(results) > 0:
		image = results[0]
		#tag = '<img class="tileImage" src="' + image.getURL() + "/image_preview" + '" />'
		obj = image.getObject()
		if hasattr(obj, "tag"):
		    tag = obj.tag(scale='preview', css_class='tileImage hidden')
		    return tag
		return ""
	return ""
    
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
    
    def isVideo(self, item):
	result = IFlowPlayable.providedBy(item)
	return result

    def audio_only(self, item):
	result = IAudio.providedBy(item)
	return result