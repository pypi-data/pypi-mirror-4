###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################


import re

from zope.component.interfaces import IFactory
from zope.interface import implements, implementedBy

from zopyx.txng3.core.interfaces import ISplitter
from zopyx.txng3.ext.splitter import Splitter as _Splitter


class Splitter:
    """ A wrapper for TXNGSplitter """

    implements(ISplitter)

    def __init__(self, *args, **kw):
        self._splitter = _Splitter(**kw)

    def split(self, content):
        return self._splitter.split(content)


class SplitterFactory:
    
    implements(IFactory)

    def __call__(self, maxlen=64, singlechar=True, casefolding=True, separator='+'):
        splitter = Splitter(maxlen=maxlen, singlechar=singlechar, casefolding=casefolding, separator=separator)
        return splitter

    def getInterfaces(self):
        return implementedBy(Splitter)

SplitterFactory = SplitterFactory()


# patterns used by the splitter (will be compiled to regexes)
SPLIT_AT = '\s|\t'
PUNCTUATION = '\.|,|\?|\!|:|;|"'
ADDITIONAL_CHARS = '\-'
RE_FLAGS = re.I | re.M | re.UNICODE


class SimpleSplitter:
    """ A simple unicode-aware splitter """

    implements(ISplitter)

    def __init__(self, 
                 casefolding=1, 
                 split_at=SPLIT_AT, 
                 punctuation=PUNCTUATION, 
                 additional_chars=ADDITIONAL_CHARS,
                 *args, **kw):
        """ 'split_at' -- a regular expression that is used to split strings.
            The regular expression is passed unchanged to re.compile().
        """

        self.splitter = re.compile(split_at, RE_FLAGS)
        self.punctuation = punctuation
        self.casefolding = casefolding
        self.regex = re.compile(r'\w+[\w%s]*' % additional_chars, RE_FLAGS)

    def split(self, content):
        """ Split a text string (prefered unicode into terms according to the
            splitter regular expression.
        """
        if self.casefolding:
            content = content.lower()
        terms = [t.strip(self.punctuation) for t in self.splitter.split(content)]
        terms = [t.replace('_', '') for t in terms]
        terms = [''.join(self.regex.findall(t)) for t in terms]
        terms = [t for t in terms if t]
        return terms


class SimpleSplitterFactory:
    
    implements(IFactory)

    def __call__(self, split_at=SPLIT_AT, punctuation=PUNCTUATION, *args, **kw):
        return SimpleSplitter(split_at=split_at, punctuation=punctuation, *args, **kw)

    def getInterfaces(self):
        return implementedBy(SimpleSplitter)

SimpleSplitterFactory = SimpleSplitterFactory()
