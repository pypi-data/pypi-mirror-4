###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

from zope.interface import Interface

class IStopwords(Interface):
    """ interface for a stopword utility"""

    def stopwordsForLanguage(language):    
        """ return all stopwords for a given language (by country code) as list
        """

    def process(words, language):   
        """ filter out all stopwords for a given language from a sequence of words """

    def availableLanguages():
        """ return a list of languages for which stopword files exist """
