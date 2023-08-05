#-*- coding: iso-8859-1 -*-

###########################################################################
# TextIndexNG V 3
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

import sys, unittest

from zope.interface.verify import verifyClass

from zopyx.txng3.core.interfaces import ILexicon
from zopyx.txng3.core.exceptions import LexiconError
from zopyx.txng3.core.lexicon import Lexicon

text_en = u'the quick brown fox jumps over the lazy dog'
text_de = unicode('Bei den dreitägigen Angriffen seien auch bis auf einen alle '
                  'the Flugplätze der Taliban zerstört worden', 'iso-8859-1')

class LexiconTests(unittest.TestCase):

    def setUp(self):
        self._lexicon = Lexicon()

    def _populateLexicon(self):
        self._lexicon.addLanguage('en')
        self._lexicon.addLanguage('de')
        self._lexicon.insertWords(text_en.split(' '), 'en')
        self._lexicon.insertWords(text_de.split(' '), 'de')

    def testInterface(self):
        verifyClass(ILexicon, self._lexicon.__class__)

    def testEmpty(self):
        assert len(self._lexicon) == 0

    def testNonUnicode(self):
        self._lexicon.addLanguage('en')
        self.assertRaises(LexiconError, self._lexicon.insertWord, 'foo-bar')
        self.assertRaises(LexiconError, self._lexicon.insertWord, dict())
        self.assertRaises(LexiconError, self._lexicon.insertWord, 2)
        self.assertRaises(LexiconError, self._lexicon.insertWords, [u'a', 'b'])

    def testLanguages(self):
        assert len(self._lexicon.getLanguages()) == 0
        self._lexicon.addLanguage('de')
        self._lexicon.addLanguage('en')
        assert len(self._lexicon.getLanguages()) == 2
        self._lexicon.addLanguage('en')
        assert len(self._lexicon.getLanguages()) == 2
        langs = self._lexicon.getLanguages()
        assert 'en' in langs
        assert not 'fr' in langs
        assert self._lexicon.hasLanguage('en')
        assert self._lexicon.hasLanguage('de')
        assert not self._lexicon.hasLanguage('fr')

    def testInsert(self):
        self._populateLexicon()
        wids = [self._lexicon.getWordId(word) for word in text_en.split(' ')]
        assert wids == self._lexicon.getWordIds(text_en.split(' '))
        wids = [self._lexicon.getWordId(word) for word in text_de.split(' ')]
        assert wids == self._lexicon.getWordIds(text_de.split(' '))

    def testWids(self):
        words = text_de.split(' ')
        self._lexicon.addLanguage('de')

        d = {}
        for word, wid in zip(words, self._lexicon.insertWords(words, 'de')):
            d[word] = wid

        for word, wid in d.items():
            self.assertEqual(self._lexicon.getWordAndLanguage(wid), (word, 'de'))
            self.assertEqual(self._lexicon.getWord(wid), word)

    def testGetWordForLanguage(self):
        L = Lexicon()
        L.addLanguage('en')
        L.addLanguage('de')
        L.insertWords((u'fox', u'quick'), 'en')
        L.insertWords((u'fuchs', u'quick'), 'de')
        en_words = L.getWordsForLanguage('en')
        en_words.sort()
        de_words = L.getWordsForLanguage('de')
        de_words.sort()
        self.assertEqual(en_words, ['fox', 'quick'])
        self.assertEqual(de_words, ['fuchs', 'quick'])
        self.assertRaises(LexiconError, L.getWordsForLanguage, 'unsupported_language')

    def testLanguageDependentRetrival(self):
        self._populateLexicon()
        gw = self._lexicon.getWordId
        assert gw('the', 'en') != None
        assert gw('the', 'de') != None
        assert gw('einen', 'en') == None
        assert gw('einen', 'de') != None
        assert gw('the', 'en') != gw('the', 'de') 

    def testRightTruncation(self):

        def _check(term, expected, language='en'):
            r1 = list(M(term, language))
            r1.sort()
            r2 = list(expected)
            r2.sort()
            self.assertEqual(r1, r2, 'got: %s, expected %s' % (repr(r1), repr(r2)))

        self._populateLexicon()
        M = self._lexicon.getWordsForRightTruncation
        _check(u't', ['the'])     
        _check(u'th', ['the'])     
        _check(u'the', ['the'])     
        _check(u'thee', [])     
        _check(u'q',  ['quick'])     
        _check(u'f', ['fox'])     
        _check(u'fo', ['fox'])     

    def testLeftTruncation(self):

        def _check(term, expected, language='en'):
            r1 = list(M(term, language))
            r1.sort()
            r2 = list(expected)
            r2.sort()
            self.assertEqual(r1, r2, 'got: %s, expected %s' % (repr(r1), repr(r2)))

        self._populateLexicon()
        M = self._lexicon.getWordsForLeftTruncation
        _check(u'the', ['the'])     
        _check(u'he', ['the'])     
        _check(u'e', ['the'])     
        _check(u'thee', [])     
        _check(u'ick',  ['quick'])     
        _check(u'x', ['fox'])     
        _check(u'ox', ['fox'])     


    def testPatternMatching(self):

        def _check(term, expected, language='en'):
            r1 = list(M(term, language))
            r1.sort()
            r2 = list(expected)
            r2.sort()
            self.assertEqual(r1, r2, 'got: %s, expected %s' % (repr(r1), repr(r2)))

        self._populateLexicon()
        M = self._lexicon.getWordsForPattern
        _check(u't*', ['the'])     
        _check(u'th*', ['the'])     
        _check(u'the*', ['the'])     
        _check(u'thee*', [])     
        _check(u'q*',  ['quick'])     
        _check(u'f*', ['fox'])     
        _check(u'fo*', ['fox'])     
        _check(u'f?x', ['fox'])     
        _check(u'f*x', ['fox'])     
        _check(u'f*x', [], 'de')     
        _check(u'An*', ['Angriffen'], 'de')     
        _check(u'An*n', ['Angriffen'], 'de')     
        _check(u'Ang*n', ['Angriffen'], 'de')     
        _check(u'Ang????en', ['Angriffen'], 'de')     

        self.assertRaises(LexiconError, M, '*')

    def testSimilaritySearch(self):

        def _check(term, expected, language='en'):
            r1 = list([term for term,ratio in M(term, 0.5, language=language)])
            r1.sort()
            r2 = list(expected)
            r2.sort()
            self.assertEqual(r1, r2, 'got: %s, expected %s' % (repr(r1), repr(r2)))

        self._populateLexicon()
        M = self._lexicon.getSimiliarWords
        _check(u'the', ['the'])     
        _check(u'fox', ['fox'])     
        _check(u'fux', ['fox'])     
        _check(u'Angriffe', ['Angriffen'], 'de')     
        _check(u'Angriffen', ['Angriffen'], 'de')     
        _check(u'Angrüff', ['Angriffen'], 'de')     
        _check(u'Angrüven', ['Angriffen'], 'de')     
        _check(u'Angrüvvven', ['Angriffen'], 'de')     
        _check(u'Ankreivven', ['Angriffen', 'einen', 'seien'], 'de')     

def test_suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(LexiconTests))
    return s

def main():
   unittest.TextTestRunner().run(test_suite())

def debug():
   test_suite().debug()

def pdebug():
    import pdb
    pdb.run('debug()')
   
if __name__=='__main__':
   if len(sys.argv) > 1:
      globals()[sys.argv[1]]()
   else:
      main()

