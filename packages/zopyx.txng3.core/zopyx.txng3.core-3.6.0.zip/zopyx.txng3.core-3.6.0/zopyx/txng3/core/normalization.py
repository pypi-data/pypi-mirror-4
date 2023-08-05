###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
Normalizer

$Id: normalization.py 2080 2009-03-14 11:23:05Z ajung $
"""

import os, re

from zopyx.txng3.ext import normalizer
from zope.interface import implements
from zopyx.txng3.core.interfaces import INormalizer

_dir = os.path.dirname(__file__)

nm_dir = os.path.join(os.path.dirname(__file__), 'data', 'normalizers')


class Normalizer:
    """ normalizes content based on a replacement table """

    implements(INormalizer)

    def __init__(self):
        self._cache = {}  # language -> replacement table 

    def availableLanguages(self):
        files = [f for f in os.listdir(nm_dir) if f.endswith('.txt')]
        return [os.path.splitext(f)[0] for f in files]

    def process(self, words, language): 
        if not self._cache.has_key(language):
            table = readNormalizer(language)
            self._cache[language] = normalizer.Normalizer(table)

        return self._cache[language].normalize(words)

    def translationTable(self, language):
        return readNormalizer(language)

    def __repr__(self):
        return "%s (%s)" % (self.__class__.__name__, self.availableLanguages()) 


enc_reg = re.compile('#\s*encoding\s*=\s*([\w\-]+)')

def readNormalizer(language):
    """ read a stopword file (line-by-line) from disk.
        'fname' is either relative to ./Normalizer/
        or has an absolute path.
    """

    encoding = None

    fname = os.path.join(nm_dir, '%s.txt' % language) 
    if not os.path.exists(fname):
        return []

    lst = []
    for l in open(fname): 
        if not l.strip(): continue

        mo = enc_reg.match(l)
        if mo:
            encoding= mo.group(1)
            continue

        if l.startswith('#'): continue

        fields = l.split()
        if len(fields) == 1:
            fields = (fields[0], '')  # replace XX with ''

        k = unicode(fields[0], encoding) 
        v = unicode(fields[1], encoding) 

        lst.append((k, v))

    return lst

NormalizerUtility = Normalizer()
