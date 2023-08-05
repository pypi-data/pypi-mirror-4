###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
Dumb query parsers

$Id: dumb.py 2055 2009-03-14 10:13:45Z ajung $
"""

from zope.interface import implements
from zopyx.txng3.core.interfaces import IParser 
from zopyx.txng3.core.parsetree import WordNode, OrNode, AndNode 


class DumbOrParser:
    """ A dumb query parser that take a whitespace separated list of 
        words and creates an Or query. No support for wildcards etc...
        just plain words.
    """

    implements(IParser)

    def getLanguage(self):
        return None
    
    def _parse(self, query):
        words = [w.strip() for w in query.split(' ')]
        return tuple([WordNode(w) for w in words if w])

    def parse(self, query):
        res = self._parse(query)
        if res:
            return OrNode(res)
        else:
            return None



class DumbAndParser(DumbOrParser):

    implements(IParser)

    def parse(self, query):
        res = self._parse(query)
        if res:
            return AndNode(res)
        else:
            return None
        return AndNode(self._parse(query))


DumbAndQueryParser = DumbAndParser()    
DumbOrQueryParser = DumbOrParser()

