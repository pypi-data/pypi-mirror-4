from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from collective.flowplayer.interfaces import IFlowPlayable
from Products.Archetypes.utils import shasattr
from zope.security import checkPermission

try:
    from collective.contentleadimage.config import IMAGE_FIELD_NAME
    from collective.contentleadimage.leadimageprefs import ILeadImagePrefsForm
    LEADIMAGE_EXISTS = True
except ImportError:
    LEADIMAGE_EXISTS = False   

class SearchView(BrowserView):
    def tag(self, obj, scale="thumb" ,css_class='tileImage'):
	if LEADIMAGE_EXISTS:
	    try:
		context = aq_inner(obj)
	    except:
		return ''
	    field = context.getField(IMAGE_FIELD_NAME)
	    if field is not None:
		if field.get_size(context) != 0:
		    return field.tag(context, scale=scale, css_class=css_class)
	    return ''
	else:
	    return ''
    
    def isVideo(self, item):
	result = IFlowPlayable.providedBy(item)
	return result

    def audioOnly(self, item):
	result = IAudio.providedBy(item)
 	return result

    def getTwoWayRelatedItems(self):
        result = []
        try:
            related = self.context.getRefs()
	    backRelated = self.context.getBRefs()
            workflow = getToolByName(self, 'portal_workflow')
            member = getToolByName(self, 'portal_membership') 
            
            for item in related:
                if (not self.isPublishable(item) or workflow.getInfoFor(item, 'review_state') == 'published' or not member.isAnonymousUser()):
                    if item.id != self.context.id:
                        result.append(item)
            
            for backItem in backRelated:
                if (not self.isPublishable(backItem) or workflow.getInfoFor(backItem, 'review_state') == 'published' or not member.isAnonymousUser()):
                    if backItem.id != self.context.id:
                        result.append(backItem)
                        
            return self.uniq(result)
        except:
            return result
	
    def trim_description(self, desc, num):
	if len(desc) > num: 
		res = desc[0:num]
		lastspace = res.rfind(" ")
		res = res[0:lastspace] + " ..."
		return res
	else:
		return desc

    def getSearchableTypes(self):
	ploneTypes = getToolByName(self, 'plone_utils').getUserFriendlyTypes()
	v2Types = ['All', 'Media']
	result = []
	for type in ploneTypes:
		result.append(type)
	for type in v2Types:
		result.append(type)
	
	if 'Image' in result:
		result.remove('Image')
	if 'File' in result:
		result.remove('File')
	
	clean = self.removeBlackListed(result)
	
	order = self.orderTypesList(clean)
	return order 

    def removeBlackListed(self, list):
	blackList = ['Link', 'Document', 'Favorite', 'Folder', 'FormFolder', 'Large Plone Folder', 'Topic']

	for item in blackList:
		if item in list:
			list.remove(item)
	return list

    def orderTypesList(self, list):
	order = ['All', 'News Item', 'Event', 'Media', 'Organization', 'Person', 'Work']
	result = []

	for type in order:
		if type in list:
			result.append(type)
	for extra in list:
		if extra not in result:
			result.append(extra)
	
	return result

    def purgeType(self, type):
	purgedResult = []

	if type == 'All':
		purgedResult = getToolByName(self, 'plone_utils').getUserFriendlyTypes()
	elif type == 'Media':
		purgedResult = ['File', 'Image']
	else:
		purgedResult = [type]
	
	return purgedResult

    def getTypeName(self, type):
	if((self.request['LANGUAGE'])[:2] == 'es'):
	    if type == 'Person':
		    name = 'Personas'
	    elif type == 'Event':
		    name = 'Eventos'
	    elif type == 'Organization':
		    name = 'Organizaciones'
	    elif type == 'Work':
		    name = 'Obras'
	    elif type == 'All':
		    name = 'Todo'
	    elif type == 'Media':
		    name = 'Media'
	    elif type == 'News Item':
		    name = 'Noticias'
	    else:
		    name = type + 's'
	else:
	    if type == 'Person':
		    name = 'People'
	    elif type == 'Event':
		    name = 'Events'
	    elif type == 'Organization':
		    name = 'Organizations'
	    elif type == 'Work':
		    name = 'Works'
	    elif type == 'All':
		    name = 'All'
	    elif type == 'Media':
		    name = 'Media'
	    elif type == 'News Item':
		    name = 'News'
	    else:
		    name = type + 's'

        return name

    def canModifyContent(self, item=None):
	if item is None:
	    return checkPermission('cmf.ModifyPortalContent', self.context)
	else:
	    return checkPermission('cmf.ModifyPortalContent', item)

    def createSearchURL(self, request, type):
	purgedType = self.purgeType(type)
	portal_url = getToolByName(self, 'portal_url')
	
 
	stext = request.form.get('SearchableText', '')	

	searchURL = portal_url() + '/search?SearchableText=' + stext

	for item in purgedType:
		searchURL += '&portal_type%3Alist=' + item
	
	return searchURL
    
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
	
