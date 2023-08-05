# -*- coding: iso-8859-15 -*-

###########################################################################
# TextIndexNG V 3
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
converters unit tests

$Id: testConverters.py 2054 2009-03-14 10:11:29Z ajung $
"""

import sys, unittest, os

from zopyx.txng3.core.converters import html, sgml, ooffice, pdf


class ConverterTests(unittest.TestCase):

    def testHTML(self):
        doc = u'<html><body> alle Vögel Über Flügel und Tümpel</body></html>'
        utf8doc = u'alle Vögel Über Flügel und Tümpel'.encode('utf-8')
        C = html.Converter()
        text,enc = C.convert(doc, 'iso-8859-15', 'text/html')
        text = text.strip()
        self.assertEqual(enc, 'utf-8')
        self.assertEqual(text, utf8doc)

        text, enc = C.convert(doc.encode('utf-8'), 'utf8', 'text/html')
        text = text.strip()
        self.assertEqual(enc, 'utf-8')
        self.assertEqual(text, utf8doc)

        text, enc = C.convert(doc, 'unicode', 'text/html')
        text = text.strip()
        self.assertEqual(enc, 'utf-8')
        self.assertEqual(text, utf8doc)

    def testHTMLWithEntities(self):
        doc = u'<html><body> alle V&ouml;gel &Uuml;ber Fl&uuml;gel und T&uuml;mpel</body></html>'
        utf8doc = u'alle Vögel Über Flügel und Tümpel'.encode('utf-8')

        C = html.Converter()
        text,enc = C.convert(doc, 'iso-8859-15', 'text/html')
        text = text.strip()
        self.assertEqual(enc, 'utf-8')
        self.assertEqual(text, utf8doc)

        text, enc = C.convert(doc.encode('utf-8'), 'utf8', 'text/html')
        text = text.strip()
        self.assertEqual(enc, 'utf-8')
        self.assertEqual(text, utf8doc)

    def testXML(self):
        doc = '<?xml version="1.0" encoding="iso-8859-15" ?><body> alle Vögel Über Flügel und Tümpel</body>'
        utf8doc = u'alle Vögel Über Flügel und Tümpel'.encode('utf-8')

        C = sgml.Converter()
        # encoding should be taken from the preamble
        text,enc = C.convert(doc, 'utf8', 'text/html')
        text = text.strip()
        self.assertEqual(enc, 'utf-8')
        self.assertEqual(text, utf8doc)

    def testOpenOffice(self):
        doc = open(os.path.join(os.path.dirname(__file__), 'data', 'test.sxw'), 'rb').read()

        C = ooffice.Converter()
        # encoding should be taken from the preamble
        text, enc = C.convert(doc, 'utf8', 'text/html')
        expected = u'Viel Vögel sprangen artig in den Tüpel und über Feld und Wüste'
        expected_words = [w.strip() for w in expected.encode(enc).split() if w.strip()]
        got_words = [w.strip() for w in text.split() if w.strip()]
        self.assertEqual(got_words, expected_words)

    def testPDF(self):
        doc = open(os.path.join(os.path.dirname(__file__), 'data', 'test.pdf'), 'rb').read()

        C = pdf.Converter()
        # encoding should be taken from the preamble
        text, enc = C.convert(doc, 'utf8', 'text/html')
        expected = u'Viel Vögel sprangen artig in den Tüpel und über Feld und Wüste'
        expected_words = [w.strip() for w in expected.encode(enc).split() if w.strip()]
        got_words = [w.strip() for w in text.split() if w.strip()]
        self.assertEqual(got_words, expected_words)


def test_suite():
    return unittest.makeSuite(ConverterTests)

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
