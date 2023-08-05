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
from zopyx.txng3.core.interfaces import IThesaurus
from zopyx.txng3.core.thesaurus import Thesaurus


class ThesaurusTests(unittest.TestCase):

    def testInterface(self):
        verifyClass(IThesaurus, Thesaurus)

    def testWithExistingLanguagesNoCasefolding(self):
        T = Thesaurus('de',False)
        self.assertEqual(T.getTermsFor(u'abrechnung'), None)
        self.assertEqual(sorted(T.getTermsFor(u'Abrechnung')), [u'Berechnung', u'Bilanz', u'Faktur', u'Rechnung', u'Schlussrechnung'])

    def testWithExistingLanguagesWithCaseFolding(self):
        T = Thesaurus('de', True)
        self.assertEqual(sorted(T.getTermsFor(u'Abrechnung')), [u'berechnung', u'bilanz', u'faktur', u'rechnung', u'schlussrechnung'])
        self.assertEqual(sorted(T.getTermsFor(u'abrechnung')), [u'berechnung', u'bilanz', u'faktur', u'rechnung', u'schlussrechnung'])
        
        # make sure all words are treated synonomyous by searching for a word that is not at the beginning of the line
        #Abrechnung Berechnung, Faktur, Rechnung
        #Abrechnung Bilanz, Schlussrechnung         
        self.assertEqual(sorted(T.getTermsFor(u'Faktur')), [u'abrechnung', u'berechnung', u'rechnung'])
        self.assertEqual(sorted(T.getTermsFor(u'faktur')), [u'abrechnung', u'berechnung', u'rechnung'])

    def testFilenameConstructor(self):
        filename = os.path.join(os.path.dirname(__file__), 'data', 'thesaurus_de.txt')
        T = Thesaurus('de', filename=filename)
        self.assertEqual(sorted(T.getTermsFor(u'foo')), [u'bar', u'baz'])
    
    
    def testWithNonExistingThesaurus(self):
        T = Thesaurus('foobar')
        self.assertRaises(ValueError, T._load)
        
        T = Thesaurus('en', filename='non/existent/path')
        self.assertRaises(ValueError, T._load)

def test_suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(ThesaurusTests))
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

