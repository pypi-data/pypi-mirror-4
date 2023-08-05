from Products.Five import BrowserView
from AccessControl import getSecurityManager

class PortletView(BrowserView):
    
    def showManageButton(self):
        secman = getSecurityManager()
        if not secman.checkPermission('Portlets: Manage portlets', self.context):
            return False
        else:
            return True