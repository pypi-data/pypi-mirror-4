###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################


class SearchRequest:
    """ container for query parameters """

    def __init__(self, index, **kw):
        self.index = index
        self.__dict__.update(kw)

    def getIndex(self):
        return self.index

    def __repr__(self):
        return '%s (%s)' % (self.__class__.__name__, ', '.join(['%s=%s' % (k,v) for k,v in self.__dict__.items()]))

