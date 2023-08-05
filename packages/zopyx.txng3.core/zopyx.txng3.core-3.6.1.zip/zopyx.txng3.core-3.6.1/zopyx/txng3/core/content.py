###########################################################################
# TextIndexNG V 3
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
Content extraction

$Id: content.py 2167 2009-04-22 19:54:36Z yvoschu $
"""

import warnings

from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError
from zope.interface import implements

from zopyx.txng3.core.interfaces import IConverter
from zopyx.txng3.core.interfaces import IIndexContentCollector, IIndexableContent
from config import DEFAULT_LANGUAGE, DEFAULT_ENCODING
from compatible import callable
from logger import LOG


class IndexContentCollector:

    implements(IIndexContentCollector)

    def __init__(self):
        self._d = {}

    def addContent(self, field, text, language=None):
        if not isinstance(text, unicode):
            raise ValueError("Argument for 'text' must be of type unicode (got: %s)" % type(text))
    
        infos = self._d.get(field, ())
        self._d[field] = infos + ({'content': text, 'language': language},)

    def addBinary(self, field, data, mimetype, encoding=None, language=None,
                  logError=False, raiseException=False):
        
        try:
            converter = getUtility(IConverter, mimetype)
        except ComponentLookupError:
            LOG.warn('No converter registered for %s' % mimetype)
            return

        

        text, encoding = converter.convert(data, encoding, mimetype,
                                           logError, raiseException)

        # The result should be string/unicode. If not, convert the returned
        # content to unicode using the returned encoding. The converter is
        # in charge to handle encoding issues correctly.

        assert isinstance(text, basestring)
        if isinstance(text, str):
            text = unicode(text, encoding, 'ignore')

        infos = self._d.get(field, ())
        self._d[field] = infos + ({'content': text, 'language': language},)

    def getFields(self):
        return self._d.keys()

    def getFieldData(self, field):
        return self._d[field]

    def __nonzero__(self):
        return len(self._d) > 0 


def extract_content(fields, obj, default_encoding=DEFAULT_ENCODING, default_language=DEFAULT_LANGUAGE):   
    """ This helper methods tries to extract indexable content from a content 
        object in different ways. First we try to check for ITextIndexable
        interface or ITextIndexableRaw interfaces which are the preferred 
        way to interace with TextIndexNG indexes. Otherwise we fall back
        to the standard Zope 2 behaviour and try to get the content by
        looking at the corresponding attributes or methods directly.
        Please note that this method will not contain content-type
        specific extraction code. This should be handled in every case by
        the content-type implementation itself or through an adapter.
    """

    adapter = IIndexableContent(obj, None)
    if adapter:
        # the official TXNG3 indexer API

        icc = adapter.indexableContent(fields)

    elif hasattr(obj, 'txng_get'):

        # old Zope behaviour for objects providing the txng_get() hook
        warnings.warn('Using the txng_get() hook for class %s is deprecated.'
                      ' Use IndexContentCollector implementation instead' % obj.__class__.__name__, 
                       DeprecationWarning, 
                       stacklevel=2)
          
        result = obj.txng_get(fields)
        if result is None:
            return None

        # unpack result triple
        source, mimetype, encoding = result
        icc = IndexContentCollector()
        icc.addBinary(fields[0], source, mimetype, encoding, default_language)

    else:

        # old Zope 2 behaviour: look up value either as attribute of the object
        # or as method providing a return value as indexable content

        d = {}

        icc = IndexContentCollector()

        for f in fields:
            
            v = getattr(obj, f, None)
            if not v: continue
            if callable(v):
                v = v()

            # accept only a string/unicode string    
            if not isinstance(v, basestring):
                raise TypeError('Value returned for field "%s" must be string or unicode (got: %s, %s)' % (f, repr(v), type(v)))

            if isinstance(v, str):
                v = unicode(v, default_encoding, 'ignore')
        
            icc.addContent(f, v, default_language)

    return icc or None
