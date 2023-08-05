
def reindexMedia(object, event):
    """
        reindexes Media catalog indexes on the parent
    """
    object.reindexObject(idxs=["hasMedia"])
    object.reindexObject(idxs=["leadMedia"])
    
    