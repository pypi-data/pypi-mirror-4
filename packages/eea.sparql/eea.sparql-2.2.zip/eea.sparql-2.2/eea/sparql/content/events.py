""" Handle events
"""

def bookmarksfolder_added(obj, evt):
    """On new bookmark folder automatically fetch all queries"""
    obj.syncQueries()