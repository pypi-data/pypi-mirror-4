###########################################################################
# TextIndexNG V 3
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
ResultList

$Id: resultset.py 2238 2010-04-07 13:00:36Z zagy $
"""

from zope.interface import implements
from BTrees.IIBTree import IIBucket, intersection, union, difference

from docidlist import DocidList
from wordlist import WordList
from zopyx.txng3.core.interfaces import IResultSet

from ranking import cosine_ranking
from config import DEFAULT_LANGUAGE

class ResultSet:
    """ A datastructure to store results from subqueries """

    implements(IResultSet)

    def __init__(self, docids, words):
        self.docids = docids        # sequence of document ids
        self.words = words          # sequence of tuples (word, field)
        self.ranked_results = None

    def __repr__(self):
        return '%s(%s), %s' % (self.__class__.__name__, self.docids, [ (w,f) for w,f in self.words])

    def getWords(self):
        return self.words

    def getDocids(self):
        return self.docids

    def ranking(self, ranking_function, index, language=DEFAULT_LANGUAGE,
                nbest=50):
        self.ranked_results = ranking_function(index, self, language, nbest)

    def cosine_ranking(self, index, language=DEFAULT_LANGUAGE, nbest=50):
        # BBB, fall back to cosine ranking
        self.ranking(cosine_ranking, index, language, nbest)


    def getRankedResults(self):
        return self.items()

    def values(self):
        """ just implement the values() method to make the stupid
            ZCatalog happy to be able to call the items() method to
            obtain a sequence of (docid, score) tuples.
        """
        pass

    def items(self):
        d = IIBucket()
        if self.ranked_results:
            max = self.ranked_results[0][1]
            for k,v in self.ranked_results:
                if max == 0:
                    d[k] = 0
                else:
                    d[k] = int(v / max * 1024.0)
        return d


################################################################
# some methods of create new result sets from existing ones
################################################################

def intersectionResultSets(sets):
    """ perform intersection of ResultSets """

    if not sets:
        return ResultSet(DocidList(), WordList())

    docids = sets[0].getDocids()
    words = WordList(sets[0].getWords())

    for set in sets[1:]:
        docids = intersection(docids, set.docids)
        words.extend(set.words)
    return ResultSet(docids, words)


def unionResultSets(sets):
    """ perform intersection of ResultSets """

    docids = DocidList()
    words = WordList()
    for set in sets:
        docids = union(docids, set.docids)
        words.extend(set.words)
    return ResultSet(docids, words)


def inverseResultSet(all_docids, set):
    """ perform difference between all docids and a resultset """
    docids = difference(DocidList(all_docids), set.getDocids())
    return ResultSet(docids, set.getWords())
