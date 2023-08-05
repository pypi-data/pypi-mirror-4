###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

from zope.interface import Interface

class INormalizer(Interface):
    """ interface for normalizers"""

    def availableLanguages():    
        """ return a list of languages supported by the normalizer """

    def process(words, language):   
        """ Normalize a word or a sequence of words. Returned the normalized word
            or a sequence of normalized words. If there is no normalizer available
            for a language then the data is returned unchanged.
        """

    def translationTable(language):
        """ return the translation table for a given language where the 
            translation table is represented as list of tuples (from_str, repl_str)
        """
