from zope.interface import Interface

class  ICanContainMedia(Interface):
    """
    This is a marker interface that aplies to all 
    """
    def getMedia(self):
        """
        Gets all media inside the folder
        """
        
    def hasMedia(self):
        """
        Checks if the current folder has media inside
        """
        
    def getLeadMedia(self):
        """
        Get the lead media
        """
        
    def markLeadMedia(self, item):
        """
        Mark item as being the lead media of the current folder. unMark any other that might have the same interface.
        """
    
    def unmarkLeadMedia(self, item):
        """
        Remove the marker interface from item if it exists.
        """
        
class IsLeadMedia(Interface):
    """
    This is a marker interface for the item that should be shown as representative media of the folder.
    It should only mark on item on each folderish content item.
    """