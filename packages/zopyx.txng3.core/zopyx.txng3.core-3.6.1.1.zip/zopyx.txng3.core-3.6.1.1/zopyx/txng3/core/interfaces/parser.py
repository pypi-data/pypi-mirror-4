###########################################################################
# TextIndexNG V 3 
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

from zope.interface import Interface

class IParser(Interface):
    """ interface for TextIndexNG query parsers """

    def getLanguage():       
        """ return language handled by the parser """

    def parse(query):
        """ Translate the 'query' into a parsetree structure. A parser should return
            None for empty queries and raise a QueryParserError exception for parser
            errors.
        """
