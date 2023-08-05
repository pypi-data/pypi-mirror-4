##########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

import sys, unittest 
from sets import Set
from random import randint

from zope.interface.verify import verifyClass

from zopyx.txng3.core.interfaces import IStorage, IStorageWithTermFrequency
from zopyx.txng3.core.storage import Storage, StorageWithTermFrequency, StorageException

class StorageBaseTests(unittest.TestCase):

    def setUp(self):
        self._storage = Storage()

    def testInterface(self):
        verifyClass(IStorage, Storage)

    def testSimple(self):
        S = self._storage
        self.assertEqual(len(S), 0)
        S.insertDocument(1, (1,2,3,4,5))
        S.insertDocument(2, (3,4,5,6,7))
        self.assertEqual(len(S), 2)
        self.assertEqual(list(S.getDocIds()), list((1,2)))
        S.removeDocument(9999)
        S.removeDocument(2)
        S.removeDocument(1)
        self.assertEqual(len(S), 0)

    def testReindex(self):
        S = self._storage
        self.assertEqual(len(S), 0)
        S.insertDocument(1, (1,2,3,4,5))
        S.insertDocument(2, (3,4,5,6,7))
        S.insertDocument(3, (3,4,22,32))
        self.assertEqual(len(S), 3)
        self.assertEqual(S.numberDocuments(), 3)
        self.assertEqual(list(S.getDocIds()), list((1,2,3)))
        S.insertDocument(3, (20,21,23))
        self.assertEqual(S.numberDocuments(), 3)
        self.assertEqual(list(S.getDocIds()), list((1,2,3)))

        self.assertEqual(list(S.getWordIdsForDocId(1)),
                         list( (1,2,3,4,5)))        
        self.assertEqual(list(S.getWordIdsForDocId(2)),
                         list( (3,4,5,6,7)))        
        self.assertEqual(list(S.getWordIdsForDocId(3)),
                         list( (20,21,23)))        

    def testReindex2(self):
        S = self._storage
        S.insertDocument(1, (0, 1))
        self.assertEqual(list(S.getWordIdsForDocId(1)), [0, 1])
        S.insertDocument(1, (0,))
        self.assertEqual(list(S.getWordIdsForDocId(1)), [0])

    def testIndexAndRemoveWithMultipleWids(self):
        S = self._storage
        self.assertEqual(len(S), 0)
        S.insertDocument(1, (1,1,2,3,4,5))
        S.removeDocument(1)   # this should not fail

    def testMultipleWids(self):
        S = self._storage
        S.insertDocument(1, (1,2,2,3,3,5))
        S.insertDocument(2, (5,5,2,2,1))
        self.assertEqual(list(S.getWordIdsForDocId(1)), list( (1,2,2,3,3,5)))        
        self.assertEqual(list(S.getWordIdsForDocId(2)), list( (5,5,2,2,1)))        
        self.assertEqual(S.numberWordsInDocument(1), 6)
        self.assertEqual(S.numberWordsInDocument(2), 5)
        S.removeDocument(2)
        self.assertRaises(StorageException, S.numberWordsInDocument, 2)
        self.assertRaises(StorageException, S.numberWordsInDocument, 99)

    def testDocids(self):
        S = self._storage
        S.insertDocument(1, (1,2,3,4,5))
        S.insertDocument(2, (3,4,5,6,7))
        S.insertDocument(3, (3,4,22,32))
        self.assertEqual(list(S.getDocumentsForWordId(5)), list( (1,2)))
        self.assertEqual(list(S.getDocumentsForWordId(3)), list( (1,2,3)))
        self.assertEqual(list(S.getDocumentsForWordId(32)), list( (3,)))
        self.assertEqual(list(S.getDocumentsForWordId(987)), list())
        self.assertEqual(list(S.getDocumentsForWordIds((3,4))), list((1,2,3)))
        self.assertEqual(list(S.getDocumentsForWordIds((5,))), list((1,2)))
        self.assertEqual(list(S.getDocumentsForWordIds(())), list())

    def testContigousWordids(self):
        S = self._storage
        S.insertDocument(1, (1,2,3,4,5,55,56))
        S.insertDocument(2, (3,4,5,56,55,7))
        S.insertDocument(3, (3,4,22,56,55,32))
        S.insertDocument(4, (55,56))
        self.assertEqual(S.hasContigousWordids(1, (55,56)), True)
        self.assertEqual(S.hasContigousWordids(2, (55,56)), False)
        self.assertEqual(S.hasContigousWordids(3, (55,56)), False)
        self.assertEqual(S.hasContigousWordids(4, (55,56)), True)
        self.assertEqual(S.hasContigousWordids(1, (3,4)), True)
        self.assertEqual(S.hasContigousWordids(2, (3,4)), True)
        self.assertEqual(S.hasContigousWordids(3, (3,4)), True)
        self.assertEqual(S.hasContigousWordids(4, (3,4)), False)

    def testGetPositions(self):
        S = self._storage
        S.insertDocument(1, (1,2,3,4,4,4,3,2,1))
        res = S.getPositions(1, 1)
        self.assertEqual(list(res), [0,8])
        res = S.getPositions(1, 2)
        self.assertEqual(list(res), [1,7])
        res = S.getPositions(1, 4)
        self.assertEqual(list(res), [3,4,5])
        res = S.getPositions(1, 99)
        self.assertEqual(list(res), [])

    def testGetPositionsRandom(self):
        S = self._storage

        for i in range(100):
            wids = []
            for j in range(200):
                wids.append(randint(0, 200))

            S.insertDocument(1, wids)

            for wid in Set(wids):
                positions = S.getPositions(1, wid)
                for pos in positions:
                    self.assertEqual(wids[pos], wid)



class StorageTests(StorageBaseTests):

    def setUp(self):
        self._storage = Storage()

    def testInterface(self):
        verifyClass(IStorage, Storage)



class StorageWithTermFrequencyTests(StorageBaseTests):

    def setUp(self):
        self._storage = StorageWithTermFrequency()

    def testInterface(self):
        verifyClass(IStorageWithTermFrequency, StorageWithTermFrequency)


    def testSimpleFrequency(self):
        S = self._storage
        S.insertDocument(1, (1,2,3))
        S.insertDocument(2, (1,))
        S.insertDocument(3, (1,1))

        F = S.getTermFrequency()

        self.assertAlmostEqual(F[1][1], 1)
        self.assertAlmostEqual(F[1][2], 1)
        self.assertAlmostEqual(F[2][1], 1)
        self.assertAlmostEqual(F[3][1], 2)


    def testSimpleFrequencyAndRemoval(self):
        S = self._storage
        F = S.getTermFrequency()
        S.insertDocument(1, (1,2,3))
        S.insertDocument(2, (1,))
        self.assertEqual(bool(F.has_key(1)), True)
        self.assertEqual(bool(F.has_key(2)), True)
        S.removeDocument(1)
        S.removeDocument(2)
        self.assertEqual(bool(F.has_key(1)), False)
        self.assertEqual(bool(F.has_key(2)), False)

    def test_hasContigousWordids(self):
        S = self._storage
        S.insertDocument(1, (0x81,))
        self.assert_(not S.hasContigousWordids(1, (0x1,)))
        S.insertDocument(1, (0x1,))
        self.assert_(S.hasContigousWordids(1, (0x1,)))
        S.insertDocument(1, (0x1, 0x81,))
        self.assert_(S.hasContigousWordids(1, (0x1,)))


def test_suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(StorageTests))
    s.addTest(unittest.makeSuite(StorageWithTermFrequencyTests))
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

