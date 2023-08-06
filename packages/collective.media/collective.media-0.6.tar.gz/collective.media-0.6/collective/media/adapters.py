from zope.interface import implements
from collective.media.interfaces import ICanContainMedia
from Products.CMFCore.utils import getToolByName

class MediaHandling(object):
    """
    Handling media actions
    """
    implements(ICanContainMedia)
    
    def __init__(self, context):
        """
           Initialize our adapter
        """
        self.context = context
    
    def getMedia(self):
        """
        Gets media on the folderish item
        """
        item = self.context
        results = []
        
        catalog = getToolByName(self.context, 'portal_catalog')
        plone_utils = getToolByName(self.context, 'plone_utils')
        path = '/'.join(item.getPhysicalPath())
        
        if item.portal_type == "Folder" or (item.restrictedTraverse('@@plone').isStructuralFolder() and item.portal_type != "Collection"):
            results = catalog.searchResults(path = {'query' : path}, type = ['Image', 'Link'], sort_on = 'getObjPositionInParent')
        elif item.portal_type == "Collection":
            results = item.queryCatalog()
            
        resultArray = []
        
        for res in results:
            if res.portal_type == "Image":
                resultArray.append(res)
            elif res.portal_type == "Link" and (res.getRemoteUrl.find("youtube.com") > -1 or res.getRemoteUrl.find("vimeo.com") > -1):
                resultArray.append(res)
            elif item.portal_type == "Collection" and res.hasMedia and res.portal_type != "Collection":
                #If the item is a collection then we need to look inside of all items manually to find media
                resultArray.append(ICanContainMedia(res.getObject()).getLeadMedia())
        
        return resultArray
    
    def hasMedia(self):
        """
        Check if item has media
        """
        return len(self.getMedia()) > 0
    
    def getLeadMedia(self):
        """
        Get the lead media
        """
        media = self.getMedia()
        if len(media) > 0:
            #TODO: This gathers only Images for now. Need to add video support
            for item in media:
                if item.portal_type == "Image":
                    return item
        
        return None
    
    def markLeadMedia(self, item):
        """
        Mark item as being the lead media of the current folder. unMark any other that might have the same interface.
        """
        #TODO: Mark the lead media here
    
    def unmarkLeadMedia(self, item):
        """
        Remove the marker interface from item if it exists.
        """
        #TODO: unmark the lead media here
    