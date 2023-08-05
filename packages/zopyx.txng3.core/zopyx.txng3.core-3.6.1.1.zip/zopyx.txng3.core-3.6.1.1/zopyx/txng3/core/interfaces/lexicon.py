###########################################################################
# TextIndexNG V 3
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

from zope.interface import Interface

class ILexicon(Interface):
    """ Interface for Lexicon objects. A TextIndexNG3 lexicon act as a storage
        for multilingual content. Words are stored per-language. 
    """

    def getLanguages():
        """ return a list of languages handled by the lexicon """

    def addLanguage(language):
        """ prepare lexicon to store words in a new language """

    def hasLanguage(language):
        """ check if the lexicon is configured for a language """

    def insertWords(words, language):
        """ Insert a sequence of words for a given language.  Return a sequence of wordids. """

    def insertWord(word, language):
        """ Insert a word for a given language. Return a wordid. """

    def getWord(wordid):
        """ return the word for the given wordid """

    def getWordId(word, language='xx'):
        """ return the word id for a given word """

    def getWordIds(words, language='xx'):
        """ return a list of wordid for a list for words """

    def getWordsForLanguage(language):
        """ return all words for a given language """

    def getWordAndLanguage(wordid):
        """ return the (word, language) tuple  for the given wordid """

    def getWordsForRightTruncation(prefix, language='en'):
        """ return a sequence of words with a given prefix """

    def getWordsForLeftTruncation(suffix , language='en'):
        """ return a sequence of words with a given suffix"""

    def getWordsForPattern(pattern, language='en'):
        """ return a sequence of words that match 'pattern'.  'pattern' is a
            sequence of characters including the wildcards '?' and '*'.
        """         

    def getWordsInRange(w1, w2, language='en'):
        """ return a sorted list of words where w1 <= w(x) <= w2  """

    def getSimiliarWords(term, threshold, language='en'):
        """ return a list of that are similar based on a similarity measure"""

    def getWordsForSubstring(sub, language='en'):
        """ return all words that match the given substring """

