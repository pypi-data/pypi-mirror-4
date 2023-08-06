
def reindexMedia(object, event):
    """
        reindexes Media catalog indexes on the parent
    """
    print "reindexing %s"%object.id
    object.reindexObject(idxs=["hasMedia"])
    object.reindexObject(idxs=["leadMedia"])
    
    