###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

from zope.interface import Interface

class IStorage(Interface):
    """ interface for storages to keep the mapping wordId to sequence
        of document ids and vis-versa.
    """

    def insertDocument(docid, WidList):
        """ Inserts or replaces a list of wordids (WidList instance)
            for a given document id
        """
    def removeDocument(docid):
        """ remove a document and all its words from the storage """

    def numberDocuments(): 
        """ return number of documents """
    
    def getDocIds(): 
        """ return all document Ids as DocidList instance"""

    def getDocumentsForWordId(wordid):
        """ return a sequence of document is as an instance of DocidList.
        """

    def getDocumentsForWordIds(wordidlist):
        """ return a sequence of document is as an instance of DocidList for
            a given list of wordids.
        """

    def getWordIdsForDocId(docid):
        """ return a sequence of word ids as WidList instance for a given
            document id
        """

    def hasContigousWordids(docid, wordids):
        """ check if a document given by its docid has given sequence of 
            wordids as contigous list.
        """

    def getPositions(docid, wordid):
        """ Return all positions of the a word given by its 'wordid'
            in a document given by its 'docid'. The position list is
            returned a sequence of ordered integers.
        """

    def numberWordsInDocument(docid):
        """ Return the total number of words within a document """


class IStorageWithTermFrequency(IStorage):
    """ Storage that keeps information about the term-per-document frequency """

    def getTermFrequency():
        """  returns the two-level mapping docid -> wids -> #(occurences of wid in docid) """
