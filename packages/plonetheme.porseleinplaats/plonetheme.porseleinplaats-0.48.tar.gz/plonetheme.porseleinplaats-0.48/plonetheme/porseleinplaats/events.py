from plone.i18n.normalizer import idnormalizer
from zope.app.component.hooks import getSite

from Products.CMFCore.utils import getToolByName
        
def objectModified(object, event):
    """
    Object was added, check for images and add them;
    """
    #print "REQUEST OBJECT %s MODIFIED"%(object.id)
    
    for i in range(1,4):
        if hasattr(object.REQUEST, 'image%s'%i) and object.REQUEST['image%s'%i][0]:
            id = idnormalizer.normalize(unicode(object.REQUEST['image%s'%i][0].filename, "utf-8"))
            
            if not hasattr(object, id):
                #print "id is new"
            
                object.invokeFactory(
                        type_name="Image",
                        id=id,
                        title=object.REQUEST['image%s'%i][0].filename
                        )
            
                item1 = object[id]
                #item1 = portal[id]
                imageData = object.REQUEST['image%s'%i][0].read()
                item1.edit(file=imageData)
                
                #item1.processForm()
            
        #else:
            #print "empty file"
            
    #Publish member folder automatically
    parent = object.aq_parent
    portal = getSite()
    wtool = getToolByName(portal, "portal_workflow")
    if wtool.getInfoFor(parent, 'review_state', '') != 'published':
        wtool.doActionFor(parent, "publish", comment="Content automatically published")
    