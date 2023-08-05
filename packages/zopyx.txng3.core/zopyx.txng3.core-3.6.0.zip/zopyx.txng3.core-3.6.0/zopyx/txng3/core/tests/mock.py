# -*- coding: iso-8859-15 -*-

###########################################################################
# TextIndexNG V 3
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
test mockups

$Id: mock.py 2054 2009-03-14 10:11:29Z ajung $
"""

import os
from zope.interface import implements, Interface
from zopyx.txng3.core.interfaces import IIndexableContent
from zopyx.txng3.core.content import IndexContentCollector as ICC


class IStupidMock(Interface):
    """ the stupid mock interface """

    def i_am_stupid():
        """ bla bla """


class StupidMock:
    """ Mockup class to check content extraction """

    implements(IStupidMock)

    def __init__(self, language, **kw):
        self.language = language
        self.__dict__.update(kw)

    def i_am_stupid(self):
        return None


class StupidMockAdapter:

    implements(IIndexableContent)

    def __init__(self, context):
        self.context = context

    def indexableContent(self, fields):
        icc = ICC()
        icc.addContent('SearchableText', u'i am so stupid', 'en')
        return icc


class Mock:
    """ Mockup class to check content extraction """

    implements(IIndexableContent)

    def __init__(self, language, **kw):
        self.language = language
        self.__dict__.update(kw)

    def indexableContent(self, fields):
        icc = ICC()
        for f in fields:
            if self.__dict__.has_key(f):
                icc.addContent(f, self.__dict__[f], self.language)
        return icc


class MockPDF:
    """ Mockup class to check content extraction """

    implements(IIndexableContent)

    def __init__(self, filename):
        self.filename = filename

    def indexableContent(self, fields):

        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, self.filename)
        if 'SearchableText' in fields:
            icc = ICC()
            icc.addContent('SearchableText', u'Die Vögel', 'de')
            icc.addBinary('SearchableText',
                          open(filename, 'rb').read(),
                          'application/pdf',
                          'iso-8859-15',
                          None)
            return icc

        return None


class MockOld:
    """ Mockup class to emulate old Z2 indexing behaviour """

    text = 'The quick brown fox jumps over the lazy dog'

    def SearchableText(self):
        return self.text
