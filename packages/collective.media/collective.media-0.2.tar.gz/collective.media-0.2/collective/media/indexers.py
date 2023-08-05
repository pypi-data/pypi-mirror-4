from plone.indexer.decorator import indexer
from collective.media.interfaces import ICanContainMedia
from Products.CMFCore.interfaces import IFolderish

@indexer(IFolderish)
def folderish_hasMedia(object, **kw):
    return ICanContainMedia(object).hasMedia();
    
@indexer(IFolderish)
def folderish_getLeadMedia(object, **kw):
    lead = ICanContainMedia(object).getLeadMedia()
    if lead is not None:
        return lead.getURL();
    else:
        return None;