###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
Query evaluator

$Id: evaluator.py 2309 2011-03-20 19:48:27Z ajung $
"""

from zopyx.txng3.core.parsetree import *
from docidlist import DocidList
from resultset import ResultSet, unionResultSets, intersectionResultSets, inverseResultSet
from stemmer import getStemmer
from logger import LOG

class Evaluator:
    """ evaluator for ParseTree instances """

    def __init__(self, searchrequest):
        self.searchrequest = searchrequest
        self.fields = self.searchrequest.index.fields

    def _getField(self, node):
        """ return field for a given node + some checking """

        # first look in the field node directly
        field = node.getField()

        # if not look at the first parent node
        if not field:
            parent = node._parent
            if parent:
                field = parent.getField()
   
        # we got something, now check if the index is configured for this field
        if field and not field in self.fields:
            raise ValueError("Index not configured for field '%s'" % field) 

        # return the default fieldname as given through the query options
        return self.searchrequest.field

    def WordNode(self, node):
        return lookup_word(self.searchrequest, 
                           node.getValue(), 
                           self._getField(node))

    def GlobNode(self, node):
        return lookup_by_pattern(self.searchrequest, 
                                 node.getValue(),
                                 self._getField(node))

    def TruncNode(self, node):
        return lookup_by_right_truncation(self.searchrequest,   
                                          node.getValue(),
                                          self._getField(node))

    def LTruncNode(self, node):
        return lookup_by_left_truncation(self.searchrequest, 
                                         node.getValue(),
                                         self._getField(node))
    
    def SimNode(self, node):
        return lookup_by_similarity(self.searchrequest, 
                                    node.getValue(),
                                    self._getField(node))

    def SubstringNode(self, node):
        return lookup_by_substring(self.searchrequest, 
                                   node.getValue(),
                                   self._getField(node))

    def RangeNode(self, node):
        return lookup_by_range(self.searchrequest, 
                               node.getValue()[0], 
                               node.getValue()[1],
                               self._getField(node))

    def AndNode(self, node):
        sets = [self(n) for n in node.getValue()]
        return intersectionResultSets(sets) 
    
    def OrNode(self, node):
        sets = [self(n) for n in node.getValue()]
        return unionResultSets(sets) 

    def NotNode(self, node):
        return inverseResultSet(self.searchrequest.index.getStorage(self.searchrequest.field).getDocIds(), self(node.getValue()))

    def PhraseNode(self, node):
        # Dealing with PhraseNodes is somewhat tricks
        # node.getValue() should return a sequence of WordNodes representing
        # the terms of the phrase

        # first tcreate he a copy of the ordered(!) terms
        words = [n.getValue() for n in node.getValue()]

        # So first perform a simple word search for all terms
        sets = [self(n) for n in node.getValue()]

        # Now intersect the results (AND). This descreases the number of documents
        # to be checked.
        rs = intersectionResultSets(sets) 
        
        # Now check if the found documents really contain the words as phrase
        return lookup_by_phrase(self.searchrequest, 
                                rs.getDocids(), 
                                words,
                                self._getField(node))

    def NearNode(self, node):
        """ near search isn't working yet """
        word_nodes = []
        word_nodes = flatten_NearNode(node.getValue(), word_nodes)
        sets = [self(n) for n in word_nodes]
        rs = intersectionResultSets(sets) 
        raise NotImplementedError('Near search not implemented yet')

    def run(self):
        return self(self.searchrequest.parsetree)

    def __call__(self, node):
        return getattr(self, node.__class__.__name__)(node)



################################################################
# helper methods to perform a low-level word lookup 
# within the index
################################################################

def lookup_word(SR, word, field):
    index = SR.getIndex()
    lexicon = index.getLexicon()

    if index.use_stemmer:
        # Stemmer support only works with disabled autoexpansion
        S = getStemmer(SR.language)
        if S:
            word = S.stem([word])[0]

        wordid = lexicon.getWordId(word, SR.language)
        if SR.autoexpand != 'off':
            raise ValueError('auto expansion is only available without enabled stemmer support')
        _words, _wids = [word], [wordid]

    else:

        wordid = lexicon.getWordId(word, SR.language)

        # perform autoexpansion only if the length of the given term is longer or
        # equal to the autoexpand_limit configuration parameter of the index

        if (SR.autoexpand=='always' or (SR.autoexpand=='on_miss' and not wordid)) \
            and len(word) >= index.autoexpand_limit:
            # lookup all words with 'word' as prefix
            words = list(lexicon.getWordsForRightTruncation(word, SR.language))

            # obtain wordids for words
            wids = lexicon.getWordIds(words, SR.language)

            # add the original word and wordid
            wids.append(wordid)
            words.append(word)
            _words, _wids = words, wids
        else:
            _words, _wids = [word], [wordid]

    # Thesaurus handling: check if thesaurus is set to a list of configured
    # thesauruses. If yes, perform a lookup for every word and enrich the 
    # resultset

    if SR.thesaurus:
        for word in _words[:]:
            for id in SR.thesaurus:
                import zope.component
                from zopyx.txng3.core.interfaces import IThesaurus

                TH = zope.component.queryUtility(IThesaurus, id)
                if TH is None:
                    raise ValueError('No thesaurus "%s" configured' % id)

                related_terms = TH.getTermsFor(word)
                if related_terms:
                    _words.extend(related_terms)
                    wids = lexicon.getWordIds(related_terms, SR.language)
                    _wids.extend(wids)

    return ResultSet(index.getStorage(field).getDocumentsForWordIds(_wids),  [(w, field) for w in _words])

def lookup_by_right_truncation(SR, pattern, field):
    index = SR.getIndex()
    lexicon = index.getLexicon()                                
    if index.use_stemmer:
        raise ValueError('Right truncation is not supported with stemming enabled')
    words = lexicon.getWordsForRightTruncation(pattern, SR.language)
    wids = lexicon.getWordIds(words, SR.language)
    return ResultSet(index.getStorage(field).getDocumentsForWordIds(wids), [(w, field) for w in words])

def lookup_by_left_truncation(SR, pattern, field):
    index = SR.getIndex()
    lexicon = index.getLexicon()
    if index.use_stemmer:
        raise ValueError('Left truncation is not supported with stemming enabled')
    words = lexicon.getWordsForLeftTruncation(pattern, SR.language)
    wids = lexicon.getWordIds(words, SR.language)
    return ResultSet(index.getStorage(field).getDocumentsForWordIds(wids), [(w, field) for w in words])

def lookup_by_pattern(SR, pattern, field):
    index = SR.getIndex()
    lexicon = index.getLexicon()
    if index.use_stemmer:
        raise ValueError('Pattern search is not supported with stemming enabled')
    words = lexicon.getWordsForPattern(pattern, SR.language)
    wids = lexicon.getWordIds(words, SR.language)
    return ResultSet(index.getStorage(field).getDocumentsForWordIds(wids), [(w, field) for w in words])

def lookup_by_substring(SR, pattern, field):
    index = SR.getIndex()
    lexicon = index.getLexicon()
    if index.use_stemmer:
        raise ValueError('Substring search is not supported with stemming enabled')
    words = lexicon.getWordsForSubstring(pattern, SR.language)
    wids = lexicon.getWordIds(words, SR.language)
    return ResultSet(index.getStorage(field).getDocumentsForWordIds(wids), [(w, field) for w in words])

def lookup_by_similarity(SR, pattern, field):
    index = SR.getIndex()
    lexicon = index.getLexicon()
    if index.use_stemmer:
        raise ValueError('Similarity search is not supported with stemming enabled')
    words = [word for word, ratio in lexicon.getSimiliarWords(pattern, SR.similarity_ratio, SR.language)]
    wids = lexicon.getWordIds(words, SR.language)
    return ResultSet(index.getStorage(field).getDocumentsForWordIds(wids), [(w, field) for w in words])

def lookup_by_range(SR, from_word, to_word, field):
    index = SR.getIndex()
    lexicon = index.getLexicon()
    if index.use_stemmer:
        raise ValueError('Range search is not supported with stemming enabled')
    words = lexicon.getWordsInRange(from_word, to_word, SR.language)
    wids = lexicon.getWordIds(words, SR.language)
    return ResultSet(index.getStorage(field).getDocumentsForWordIds(wids), [(w, field) for w in words])

def lookup_by_phrase(SR, docids, words, field):
    index = SR.getIndex()
    lexicon = index.getLexicon()
    storage = index.getStorage(field)

    if index.use_stemmer:
        S = getStemmer(SR.language)
        if S:
            words = S.stem(words)

    wids = lexicon.getWordIds(words, SR.language)
    docids = [docid for docid in docids if storage.hasContigousWordids(docid, wids)]
    return ResultSet(DocidList(docids), [(w, field) for w in words])
