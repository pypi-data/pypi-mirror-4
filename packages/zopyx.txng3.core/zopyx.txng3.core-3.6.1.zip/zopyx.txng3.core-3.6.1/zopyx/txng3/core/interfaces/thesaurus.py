###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################


from zope.interface import Interface

class IThesaurus(Interface):
    """ interface for a multilingual thesaurus"""

    def getTermsFor(word):
        """ Returns a sequence of similar terms for 'word'.  If there are no
            matching terms then the thesaurus *must* return None.
        """    

    def getLanguage():
        """ return the language of the thesaurus """

    def getSize():
        """ return the number of entries in the thesaurus """
