###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################


"""
Component Vocabularies for the utility-adding view
of the Ting-Index.

Contributed by Frank Burkhardt

$Id: vocabulary.py 2336 2011-05-31 16:41:23Z yvoschu $
"""

import zope.interface
from zope.componentvocabulary.vocabulary import UtilityNames
from zope.schema.interfaces import IVocabularyFactory
from zopyx.txng3.core.interfaces import ISplitter, ILexicon, IStorage, IParser


def SplitterVocabulary(context):
    return UtilityNames(ISplitter)

def LexiconVocabulary(context):
    return UtilityNames(ILexicon)

def StorageVocabulary(context):
    return UtilityNames(IStorage)

def ParserVocabulary(context):
    return UtilityNames(IParser)

zope.interface.directlyProvides(
    SplitterVocabulary, IVocabularyFactory)
zope.interface.directlyProvides(
    LexiconVocabulary, IVocabularyFactory)
zope.interface.directlyProvides(
    StorageVocabulary, IVocabularyFactory)
zope.interface.directlyProvides(
    ParserVocabulary, IVocabularyFactory)
