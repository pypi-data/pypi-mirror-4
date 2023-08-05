###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
Storage of docid -> wordids mapping

$Id: storage.py 2194 2009-12-08 06:06:24Z ajung $
"""

from persistent import Persistent
from zope.interface import implements, implementedBy
from zope.component.interfaces import IFactory
from compatible import Persistent
from BTrees.IOBTree import IOBTree
from BTrees.IIBTree import IITreeSet, IIBTree, union, IISet, difference
import BTrees.Length 


from zopyx.txng3.core.interfaces import IStorage, IStorageWithTermFrequency
from zopyx.txng3.core.exceptions import StorageException
from widcode import encode , decode
from docidlist import DocidList

class _PS(Persistent):
    """ ZODB-aware wrapper for strings """

    def __init__(self, s):
        self.s = s
 
    def get(self):
        return self.s



class Storage(Persistent):
    """ storage to keep the mapping wordId to sequence
        of document ids and vis-versa.
    """

    implements(IStorage)

    def __init__(self): 
        self.clear()

    def clear(self):
        self._doc2wid = IOBTree()   # docid -> [wordids]
        self._wid2doc = IOBTree()   # wordid -> [docids]
        self._docweight = IIBTree() # docid -> (# terms in document)
        self._length = BTrees.Length.Length()
    
    def __len__(self): return self._length()
    numberDocuments = __len__

    def insertDocument(self, docid, widlist):

        if not self._doc2wid.has_key(docid):
            self._length.change(1)

        enc_widlist = encode(widlist)
        old_enc_widlist = self._doc2wid.get(docid)
        if old_enc_widlist is not None:
            old_enc_widlist = old_enc_widlist.get() # unwrap _PS instance

        removed_wordids = []
        if old_enc_widlist != enc_widlist :
            self._doc2wid[docid] = _PS(enc_widlist)
            if old_enc_widlist is not None:
                old_widlist = IISet(decode(old_enc_widlist))
                removed_wordids = difference(old_widlist, IISet(widlist))

        tree = self._wid2doc
        tree_has = tree.has_key
        count = 0
        for wid in widlist:
            count += 1
            if not tree_has(wid):
                tree[wid] = DocidList([docid])
            else:
                if not docid in tree[wid]:   
                    tree[wid].insert(docid)

        for wid in removed_wordids:
            if tree_has(wid):
                try:
                    tree[wid].remove(docid)
                except KeyError:
                    pass

        self._docweight[docid] = count

    def removeDocument(self, docid):

        try:
            wordids = self._doc2wid[docid]
        except KeyError:
            return # silently ignore 

        wordids = wordids.get() # unwrap _PS instance

        tree = self._wid2doc
        tree_has = tree.has_key
        for wordid in decode(wordids):

            if tree_has(wordid):
                try:
                    tree[wordid].remove(docid)
                except KeyError:
                    pass

                if not tree[wordid]:
                    del tree[wordid]

        del self._doc2wid[docid]
        del self._docweight[docid]
        self._length.change(-1)

    def getDocIds(self):
        return self._doc2wid.keys()

    def getDocumentsForWordId(self, wordid):
        try:
            return self._wid2doc[wordid]
        except (TypeError, KeyError):
            return DocidList()

    def getDocumentsForWordIds(self, wordidlist):

        r = DocidList()
        for wordid in wordidlist:
            try:
                docids = self._wid2doc[wordid]
            except (TypeError, KeyError):
                continue

            r = union(r, docids)
        return r

    def getWordIdsForDocId(self, docid):
        try:
            ps_wrapper = self._doc2wid[docid]
            return decode(ps_wrapper.get())
        except KeyError:
            raise StorageException('No such docid: %d' % docid)

    def numberWordsInDocument(self, docid):
        try:
            return self._docweight[docid]
        except KeyError:
            raise StorageException('No such docid: %d' % docid)


    def hasContigousWordids(self, docid, wordids):
        # *The trick* to perform a phrase search is to use the feature
        # that the string encoded wids can be searched through string.find().
        # However string.find() is not sufficient since it might find occurences
        # where the next byte does not represent the start of a new word (with
        # 7th bit set). So we must loop search until we find a hit (and we don't
        # return on the first occurence anymore)

        encoded_wids = encode(wordids)
        encoded_wids_len = len(encoded_wids)
        encoded_document = self._doc2wid[docid].get()
        encoded_document_len = len(encoded_document)

        found = False
        offset = 0

        while 1:
            pos = encoded_document[offset:].find(encoded_wids)
            
            if pos == -1: # end of string?
                break

            if pos != -1: # found something

                if offset+pos+encoded_wids_len < encoded_document_len:
                    # check if the next token represents a new word (with
                    # 7th bit set)
                    next_c = encoded_document[offset+pos+encoded_wids_len]
                    if ord(next_c) > 127:
                        # start of a new word -> we *really* found a word
                        found = True
                        break
                else:
                    # we found a word and we are the end of the complete string                    
                    found = True
                    break

            offset = offset + pos + 1

        return found


        return encoded_wids in encoded_document
    def getPositions(self, docid, wordid):
        """ return a sequence of positions of occurrences of wordid within
            a document given by its docid.
        """

        encoded_wid = encode((wordid,))
        encoded_document = self._doc2wid[docid].get()

        positions = IITreeSet()
        for pos, wid in enumerate(decode(encoded_document)):
            if wid == wordid:
                positions.insert(pos)
        return positions



class StorageWithTermFrequency(Storage):

    implements(IStorageWithTermFrequency)

    def clear(self):
        Storage.clear(self)
        self._frequencies = IOBTree()   # docid -> (wordid -> #occurences)

            
    def insertDocument(self, docid, widlist):
        Storage.insertDocument(self, docid, widlist)
                   
        occurences = {}   # wid -> #(occurences)
        num_wids = float(len(widlist))
        for wid in widlist:
            if not occurences.has_key(wid):
                occurences[wid] = 1
            else:
                occurences[wid] += 1

        self._frequencies[docid] = IIBTree()
        tree = self._frequencies[docid]
        for wid,num in occurences.items():
            tree[wid] = num


    def removeDocument(self, docid):

        # note that removing a non existing document should not
        # raise an exception
        Storage.removeDocument(self, docid)

        try:
            del self._frequencies[docid]
        except KeyError:
            pass


    def getTermFrequency(self):
        return self._frequencies
            
        
class _StorageFactory:
    
    implements(IFactory)

    def __init__(self, klass):
        self._klass = klass

    def __call__(self):
        return self._klass()

    def getInterfaces(self):
        return implementedBy(self._klass)

StorageFactory = _StorageFactory(Storage)
StorageWithTermFrequencyFactory = _StorageFactory(StorageWithTermFrequency)
