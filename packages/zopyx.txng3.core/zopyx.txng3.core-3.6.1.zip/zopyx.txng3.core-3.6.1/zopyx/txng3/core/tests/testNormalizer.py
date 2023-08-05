#-*- coding: iso-8859-1 -*-

###########################################################################
# TextIndexNG V 3
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

import sys, os, unittest

from zope.interface.verify import verifyClass

from zopyx.txng3.core.interfaces import INormalizer
from zopyx.txng3.core.normalization import Normalizer 
from zopyx.txng3.core.exceptions import NormalizerError

class NormalizerTests(unittest.TestCase):

    def testInterface(self):
        verifyClass(INormalizer, Normalizer)

    def testAvailableLanguages(self):
        N = Normalizer()
        self.assertEqual('de' in N.availableLanguages(), True)
        self.assertEqual('fr' in N.availableLanguages(), True)
        self.assertEqual('en' not in N.availableLanguages(), True)

    def testTranslationTable(self):
        N = Normalizer()
        self.assertEqual(u'ü' in  [k for (k,v) in N.translationTable('de')], True)
        self.assertEqual(u'o' not in  [k for (k,v) in N.translationTable('de')], True)
        self.assertEqual(len(N.translationTable('en')), 0)

    def testNormalizer(self):
        N = Normalizer()
        s = unicode('überhaupt Brücken Äcker und Mössingen', 'iso-8859-15')
        res = N.process(s.split(' '), 'de')
        self.assertEqual(res, [u'ueberhaupt', u'Bruecken', u'Aecker', u'und', u'Moessingen'])
        res = N.process(s.split(' '), 'en')   # unknown languages should not raise an error
        self.assertEqual(res, s.split(' '))
        self.assertEqual(N.process(u'für', 'de'), u'fuer')
        self.assertEqual(N.process([u'für'], 'de'), [u'fuer'])
        self.assertEqual(N.process(u'für', 'en'), u'für')
        self.assertEqual(N.process([u'für'], 'en'), [u'für'])
        

def test_suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(NormalizerTests))
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

