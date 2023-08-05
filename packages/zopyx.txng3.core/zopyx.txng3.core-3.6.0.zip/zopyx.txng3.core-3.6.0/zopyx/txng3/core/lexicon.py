###########################################################################
# TextIndexNG V3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

""" 
Lexicon -- maps words to word ids. Words are stored in language dependent
mapping so words can be retrieved by-language. The lexicon is completely
unicode based. This means all stored words must be unicode and all query
strings must be unicode.

$Id: lexicon.py 2080 2009-03-14 11:23:05Z ajung $
"""

import re

from BTrees.OOBTree import OOBTree
from BTrees.OIBTree import OIBTree
from BTrees.IOBTree import IOBTree
import BTrees.Length

from compatible import Persistent
from zope.component.interfaces import IFactory
from zope.interface import implements, implementedBy
from zopyx.txng3.core.interfaces import ILexicon
from zopyx.txng3.core.exceptions import LexiconError
from config import DEFAULT_LANGUAGE

try:
    from zopyx.txng3.ext.levenshtein import ratio
    have_lv = True
except ImportError:
    have_lv = False


class Lexicon(Persistent):
    """Maps words to word ids """

    implements(ILexicon)

    def __init__(self, languages=()):
        self._words = OOBTree()
        self._wids = IOBTree()   # wid -> word
        self._nextid = BTrees.Length.Length()
        for l in languages: 
            self.addLanguage(l)

    def __len__(self):
        return sum([len(tree) for tree in self._words.values()])

    def addLanguage(self, language):
        """ prepare lexicon for a new language """
        self._words[language] = OIBTree()
    
    def getLanguages(self):
        """ return sequence of languages """
        return tuple(self._words.keys())

    def hasLanguage(self, language):
        """ language handled by lexicon? """
        return bool(self._words.has_key(language))

    def _getTree(self, language):
        """ return tree for a given language """

        try:
            return self._words[language]
        except KeyError:
            raise LexiconError('Unsupported language: %s' % language)

    def insertWord(self, word, language=DEFAULT_LANGUAGE):
        """ insert a word and return the corresponding wordid """
        return self.insertWords([word], language)[0]

    def insertWords(self, words, language=DEFAULT_LANGUAGE):
        """ insert a sequence of words and return a sequence of 
            corresponding wordids.
        """
        tree = self._getTree(language)            

        wids = []
        for word in words:

            if not isinstance(word, unicode):
                raise LexiconError('Only unicode string can be indexed (%s)' % repr(word))

            try:
                wids.append(tree[word])
            except KeyError:
                wid = self._nextid()
                self._nextid.change(1)
                tree[word] = wid
                self._wids[wid] = (word, language)
                wids.append(wid)
        
        return wids

    def getWordId(self, word, language=DEFAULT_LANGUAGE):
        """ Return the wordid for a given word in a given language or None if 
            the word is not available.
        """
        tree = self._getTree(language)            
        return tree.get(word, None)

    def getWordIds(self, words, language=DEFAULT_LANGUAGE):
        """ Return sequence of wordids for a sequence of words in a given language """
        tree = self._getTree(language)            
        get = tree.get
        return [get(word, None) for word in words]        

    def getWord(self, wid):
        """ Return the word for a given wordid or None if not available """
        try:
            return self._wids.get(wid)[0]
        except KeyError:
            return None

    def getWordsForLanguage(self, language):
        """ Return all words for 'language' """
        return list(self._getTree(language))

    def getWordAndLanguage(self, wid):
        """ Return a tuple (word, language tuple) for a given wordid or None
            if not available.   
        """
        return self._wids.get(wid, None)

    def getWordsForRightTruncation(self, prefix, language=DEFAULT_LANGUAGE):
        """ Return a sequence of words with a common prefix """
        
        if not isinstance(prefix, unicode):
            raise LexiconError('Prefix must be unicode (%s)' % prefix)
        tree = self._getTree(language)            
        return  tree.keys(prefix, prefix + u'\uffff') 

    def getWordsInRange(self, w1, w2, language=DEFAULT_LANGUAGE):
        """ return all words within w1...w2 """
        if not isinstance(w1, unicode):
            raise LexiconError('1. argument must be unicode (%s)' % w1)
        if not isinstance(w2, unicode):
            raise LexiconError('2. argument must be unicode (%s)' % w2)
        tree = self._getTree(language)
        return tree.keys(w1, w2)

    def getWordsForSubstring(self, sub, language=DEFAULT_LANGUAGE):
        """ return all words that match *sub* """
        if not isinstance(sub, unicode):
            raise LexiconError('Substring must be unicode (%s)' % sub)
        tree = self._getTree(language)
        return [word for word in tree.keys() if sub in word]

    def getWordsForLeftTruncation(self, suffix, language=DEFAULT_LANGUAGE):
        """ return all words with a common suffix """
        if not isinstance(suffix, unicode):
            raise LexiconError('Suffix must be unicode (%s)' % suffix)
        tree = self._getTree(language)
        return [word for word in tree.keys() if word.endswith(suffix)]

    def _createRegex(self, pattern):
        """Translate a 'pattern into a regular expression """
        return '%s$' % pattern.replace( '*', '.*').replace( '?', '.')

    def getSimiliarWords(self, term, threshold=0.75, language=DEFAULT_LANGUAGE, common_length=-1): 
        """ return a list of similar words based on the levenshtein distance """
        if not have_lv:
            raise LexiconError('Method not allowed. Please install the Levenshtein extension properly')
        tree = self._getTree(language)
        if common_length > -1:
            prefix = term[:common_length]
            words = tree.keys(prefix, prefix + u'\uffff')
        else:
            words = tree.keys()                
        return [(w, ratio(w,term)) for w in words  if ratio(w, term) > threshold]

    def getWordsForPattern(self, pattern, language=DEFAULT_LANGUAGE):
        """ perform full pattern matching """

        # search for prefix in word
        mo = re.search('([\?\*])', pattern)
        if mo is None:
            return [] 

        pos = mo.start(1)
        if pos==0: 
            raise LexiconError('pattern "%s" should not start with a globbing character' % pattern)

        prefix = pattern[:pos]
        tree = self._getTree(language)
        words = tree.keys(prefix, prefix + u'\uffff')
        regex = re.compile(self._createRegex(pattern), re.UNICODE)
        regex_match = regex.match
        return [word  for word in words if regex_match(word)] 


class LexiconFactory:
    
    implements(IFactory)

    def __call__(self, languages=()):
        return Lexicon(languages)

    def getInterfaces(self):
        return implementedBy(Lexicon)

LexiconFactory = LexiconFactory()
