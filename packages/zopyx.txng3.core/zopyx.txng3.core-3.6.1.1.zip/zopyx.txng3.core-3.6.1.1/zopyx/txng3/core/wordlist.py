###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
WordList

$Id: wordlist.py 1572 2006-06-03 10:53:57Z ajung $
"""

from sets import Set

class WordList(Set):
    """ handles a list of words """

    def __repr__(self):
        return '%s(%s), %s' % (self.__class__.__name__, Set.__repr__(self))

    def extend(self, words):
        self.update(words)

