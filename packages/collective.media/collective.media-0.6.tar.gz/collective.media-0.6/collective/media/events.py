
def reindexMedia(object, event):
    """
        reindexes Media catalog indexes on the parent
    """
    print "Reindexing %s"%object.id
    object.reindexObject(idxs=["hasMedia"])
    object.reindexObject(idxs=["leadMedia"])
    print "Finished reindexing %s"%object.id
    
    