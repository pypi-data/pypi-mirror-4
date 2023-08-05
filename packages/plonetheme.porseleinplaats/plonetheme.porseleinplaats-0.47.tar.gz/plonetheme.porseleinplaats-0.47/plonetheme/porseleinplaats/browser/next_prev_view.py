from Products.Five import BrowserView
from Products.categorynavigator.categoryutils import CategoryUtils

class NPView(BrowserView):
    def getNext(self, subject):
        """
        Get the next subject
        """
        cu = CategoryUtils()
        cats = cu.getVTCategories()
        found = False;
        result = None
        
        for cat in cats:
            for key in cat.keywords:
                if found:
                   result = key
                   break
                elif key == subject:
                    found = True
    
        if result is not None:
            return self.context.absolute_url() +cu.generateQueryString([result,])
        else:
            return None
        
    def getPrev(self, subject):
        """
        Get the previous subject
        """
        cu = CategoryUtils()
        cats = cu.getVTCategories()
        last=None
        result = None
        
        for cat in cats:
             for key in cat.keywords:
                if key == subject:
                    result = last
                    break
                else:
                    last = key
            
        if result is not None:
            return self.context.absolute_url() +cu.generateQueryString([result,])
        else:
            return None
        
        