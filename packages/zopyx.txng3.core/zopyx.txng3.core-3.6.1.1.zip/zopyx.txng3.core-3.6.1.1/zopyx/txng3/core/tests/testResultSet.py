#-*- coding: iso-8859-1 -*-

###########################################################################
# TextIndexNG V 3
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

import sys, unittest

from zope.interface.verify import verifyClass

from zopyx.txng3.core.resultset import ResultSet, unionResultSets, intersectionResultSets, inverseResultSet
from zopyx.txng3.core.docidlist import DocidList
from zopyx.txng3.core.interfaces import IResultSet
from zopyx.txng3.core.index import Index
from zopyx.txng3.core import config

from TextIndexNGTestCase import TextIndexNGTestCase


class ResultSetTests(unittest.TestCase):

    def testInterface(self):
        verifyClass(IResultSet, ResultSet)

    def _check(self, rs, docids, words):
        rs_docids = list(rs.getDocids())
        rs_docids.sort()
        rs_words = list(rs.getWords())
        rs_words.sort()
        docids = list(docids)
        docids.sort()
        words = list(words)
        words.sort()
        self.assertEqual(rs_docids, docids)
        self.assertEqual(rs_words, words)

    def testUnion(self):
        r1 = ResultSet(DocidList((2,3,4)), ('foo', 'bar'))
        rs = unionResultSets((r1,))
        self._check(rs, (2,3,4) , ('foo', 'bar'))

        r1 = ResultSet(DocidList((2,3,4)), ('foo', 'bar'))
        r2 = ResultSet(DocidList((3,4,5)), ('dummy', 'bar'))
        rs = unionResultSets((r1, r2))
        rs2 = unionResultSets((r2, r1))
        self._check(rs, (2,3,4,5) , ('foo', 'bar', 'dummy'))
        self._check(rs2, (2,3,4,5) , ('foo', 'bar', 'dummy'))

        r1 = ResultSet(DocidList((2,3,4)), ('foo', 'bar'))
        r2 = ResultSet(DocidList(), ())
        rs = unionResultSets((r1, r2))
        rs2 = unionResultSets((r2, r1))
        self._check(rs, (2,3,4) , ('foo', 'bar'))
        self._check(rs2, (2,3,4) , ('foo', 'bar'))

        r1 = ResultSet(DocidList(), ())
        r2 = ResultSet(DocidList((2,3,4)), ('foo', 'bar'))
        rs = unionResultSets((r1, r2))
        rs2 = unionResultSets((r2, r1))
        self._check(rs, (2,3,4) , ('foo', 'bar'))
        self._check(rs2, (2,3,4) , ('foo', 'bar'))

        r1 = ResultSet(DocidList(), ())
        r2 = ResultSet(DocidList((2,3,4)), ('foo', 'bar'))
        r3 = ResultSet(DocidList((2,3,4)), ('foo', 'bar'))
        rs = unionResultSets((r1, r2, r3))
        rs2 = unionResultSets((r3, r1, r2))
        self._check(rs, (2,3,4) , ('foo', 'bar'))
        self._check(rs2, (2,3,4) , ('foo', 'bar'))

    def testIntersection(self):
        rs = intersectionResultSets(())
        self._check(rs, () , ())

        r1 = ResultSet(DocidList((2,3,4)), ('foo', 'bar'))
        rs = intersectionResultSets((r1, ))
        self._check(rs, (2,3,4) , ('foo', 'bar'))

        r1 = ResultSet(DocidList((2,3,4)), ('foo', 'bar'))
        r2 = ResultSet(DocidList((4,5,6)), ('foo', 'buzz'))
        rs = intersectionResultSets((r1, r2))
        rs2 = intersectionResultSets((r2, r1))
        self._check(rs, (4,) , ('foo', 'bar', 'buzz'))
        self._check(rs2, (4,) , ('foo', 'bar', 'buzz'))

        r1 = ResultSet(DocidList((2,3,4)), ('foo', 'bar'))
        r2 = ResultSet(DocidList(), ())
        rs = intersectionResultSets((r1, r2))
        rs2 = intersectionResultSets((r2, r1))
        self._check(rs, () , ('foo', 'bar'))
        self._check(rs2, () , ('foo', 'bar'))

        r2 = ResultSet(DocidList(), ())
        r1 = ResultSet(DocidList((2,3,4)), ('foo', 'bar'))
        rs = intersectionResultSets((r1, r2))
        rs2 = intersectionResultSets((r2, r1))
        self._check(rs, () , ('foo', 'bar'))
        self._check(rs2, () , ('foo', 'bar'))

        r1 = ResultSet(DocidList((2,3,4,5)), ('foo', 'bar'))
        r2 = ResultSet(DocidList((4,5,6)), ('foo', 'buzz'))
        r3 = ResultSet(DocidList((1,3,4,5)), ('a1', 'a2'))
        rs = intersectionResultSets((r1, r2, r3))
        rs2 = intersectionResultSets((r3, r2, r1))
        rs3 = intersectionResultSets((r3, r1, r2))
        self._check(rs, (4,5) , ('foo', 'bar', 'buzz', 'a1', 'a2'))
        self._check(rs2, (4,5) , ('foo', 'bar', 'buzz', 'a1', 'a2'))
        self._check(rs3, (4,5) , ('foo', 'bar', 'buzz', 'a1', 'a2'))

    def testInverse(self):
        all_docids = range(10)

        r = ResultSet(DocidList((2,3)), ('foo',))
        rs = inverseResultSet(all_docids, r)
        self._check(rs, (0,1,4,5,6,7,8,9) , ('foo',))

        r = ResultSet(DocidList((4,3,2)), ('foo',))
        rs = inverseResultSet(all_docids, r)
        self._check(rs, (0,1,5,6,7,8,9) , ('foo',))

        r = ResultSet(DocidList(), ('foo',))
        rs = inverseResultSet(all_docids, r)
        self._check(rs, all_docids , ('foo',))

        r = ResultSet(DocidList(all_docids), ('foo',))
        rs = inverseResultSet(all_docids, r)
        self._check(rs, (), ('foo',))


class RankingTest(TextIndexNGTestCase):

    def testRanking(self):
        r = ResultSet(DocidList((2,3)), (('foo', 5),))

        called = []
        result = object()
        def ranking_function(*args):
            called.append(args)
            return result

        index = Index()
        r.ranking(ranking_function, index)
        self.assertEquals(1, len(called))
        self.assertEquals(
            (index, r, config.DEFAULT_LANGUAGE, 50), called[0])
        self.assertEquals(result, r.ranked_results)

    def testBBBCosineRanking(self):
        r = ResultSet(DocidList((2,3)), (('foo', 5),))
        index = Index()
        r.cosine_ranking(index)


def test_suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(ResultSetTests))
    s.addTest(unittest.makeSuite(RankingTest))
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

