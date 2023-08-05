###########################################################################
# TextIndexNG V 3
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
TextIndexNG test case

$Id: TextIndexNGTestCase.py 2336 2011-05-31 16:41:23Z yvoschu $
"""

import unittest

from zope.component import provideUtility
from zope.component.interfaces import IFactory
from zope.component.testing import setUp
from zope.component.testing import tearDown

from zopyx.txng3.core.splitter import SplitterFactory, SimpleSplitterFactory
from zopyx.txng3.core.normalization import Normalizer
from zopyx.txng3.core.stopwords import Stopwords
from zopyx.txng3.core.lexicon import LexiconFactory
from zopyx.txng3.core.storage import StorageFactory
from zopyx.txng3.core.converters.pdf import PDFConverter
from zopyx.txng3.core.parsers.english import EnglishParser
from zopyx.txng3.core.interfaces import IConverter, IStopwords, INormalizer, IParser


class TextIndexNGTestCase(unittest.TestCase):
    """ base test case class for indexer related tests """

    def setUp(self):
        setUp()
        provideUtility(PDFConverter, IConverter, name='application/pdf')
        provideUtility(SplitterFactory, IFactory,
                       name='txng.splitters.default')
        provideUtility(SimpleSplitterFactory, IFactory,
                       name='txng.splitters.simple')
        provideUtility(EnglishParser(), IParser, name='txng.parsers.en')
        provideUtility(LexiconFactory, IFactory, name='txng.lexicons.default')
        provideUtility(StorageFactory, IFactory, name='txng.storages.default')
        provideUtility(Stopwords(), IStopwords)
        provideUtility(Normalizer(), INormalizer)

    def tearDown(self):
        tearDown()
