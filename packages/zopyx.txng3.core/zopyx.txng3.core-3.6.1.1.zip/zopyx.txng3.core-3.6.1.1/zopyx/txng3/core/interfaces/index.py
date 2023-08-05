###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

""" interface for Index"""

from zope.interface import Interface 

class IIndex(Interface):
    """ interface class for Index"""

    def index_object(obj, docid):
        """ indexes the object under the given 'docid' """

    def unindex_object(docid):
        """ remove the object from the index """

    def search(query, **kw): 
        """ Perform a search 'query' is the query string and **kw are optional 
            parameters specific to the index.
        """
