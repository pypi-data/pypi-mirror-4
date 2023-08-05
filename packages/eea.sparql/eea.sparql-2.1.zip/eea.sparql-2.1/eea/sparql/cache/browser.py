""" Browser
"""
import hashlib
from zope import event
from zope.component import queryMultiAdapter
from zope.lifecycleevent import ObjectModifiedEvent
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from eea.sparql.cache import InvalidateCacheEvent, cacheSparqlKey

class InvalidateMemCache(BrowserView):
    """ Invalidate memcache """

    def __call__(self):
        """ Invalidate memcache
        """
        key = cacheSparqlKey(self.context.execute_query, self.context)
        key = 'eea.sparql.content.sparql.execute_query:%s' % key
        key = hashlib.md5(key).hexdigest()
        event.notify(InvalidateCacheEvent(key=key, raw=True))
        return "Cache invalidated"

class CacheView(BrowserView):
    """ Caching for sparql query results
    """
    def __call__(self):
        if not "submit" in self.request.form:
            return self.index()

        event.notify(ObjectModifiedEvent(self.context))
        IStatusMessage(self.request).addStatusMessage("Cache invalidated")
        return self.index()

def purgeRelatedItems(obj, evt):
    """ Purge related items
    """
    getRelatedItems = getattr(obj, 'getRelatedItems', None)
    if getRelatedItems:
        for relatedItem in getRelatedItems():
            event.notify(ObjectModifiedEvent(relatedItem))

    getBRefs = getattr(obj, 'getBRefs', None)
    if getBRefs:
        for relatedItem in getBRefs():
            event.notify(ObjectModifiedEvent(relatedItem))

def purgeOnModified(obj, evt):
    """ Purge memcache on modify
    """
    request = getattr(obj, 'REQUEST', None)
    if not request:
        return

    invalidate = queryMultiAdapter((obj, request), name=u'memcache.invalidate')
    if not invalidate:
        return

    invalidate()
    purgeRelatedItems(obj, evt)
