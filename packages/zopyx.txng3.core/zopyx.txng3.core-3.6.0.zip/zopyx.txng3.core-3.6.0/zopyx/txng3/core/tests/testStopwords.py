# -*- coding: iso-8859-1 -*-

###########################################################################
# TextIndexNG V 3
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

import sys, os, unittest

from zope.interface.verify import verifyClass
from zopyx.txng3.core.interfaces import IStopwords
from zopyx.txng3.core.exceptions import StopwordError
from zopyx.txng3.core.stopwords import Stopwords, StopwordUtility 


class StopwordTests(unittest.TestCase):

    def testInterface(self):
        verifyClass(IStopwords, Stopwords)

    def testStopwords(self):
        SW = Stopwords()
        en_words = SW.stopwordsForLanguage('en')
        for w in en_words:
            self.assertEqual(type(w), unicode)            
        de_words = SW.stopwordsForLanguage('de')
        for w in de_words:
            self.assertEqual(type(w), unicode)            
        self.assertEqual(len(SW.stopwordsForLanguage('xx')), 0)

    def testProcess(self):
        SW = Stopwords()
        s = unicode('der die das mondauto foobar gehen gut und überhaupt', 'iso-8859-15')
        res = SW.process(s.split(' '), 'de')
        self.assertEqual(res, [u'mondauto', u'foobar', u'gehen', u'gut', unicode('überhaupt', 'iso-8859-15')])
        res = SW.process(s.split(' '), 'en')
        self.assertEqual(res, list(s.split(' ')))

    def testAvailableLanguages(self):
        lst = Stopwords().availableLanguages()
        assert 'en' in lst
        assert 'fr' in lst
        assert not 'xx' in lst

    def testStopwordReader(self):
        SW = Stopwords()
        for lang in SW.availableLanguages():
            words = SW.stopwordsForLanguage(lang)


def test_suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(StopwordTests))
    return s

def main():
   unittest.TextTestRunner().run(test_suite())

def debug():
   test_suite().debug()

def pdebug():
    import pdb
    pdb.run('debug()')
   
if __name__=='__main__':
   import sys
   if len(sys.argv) > 1:
      globals()[sys.argv[1]]()
   else:
      main()

