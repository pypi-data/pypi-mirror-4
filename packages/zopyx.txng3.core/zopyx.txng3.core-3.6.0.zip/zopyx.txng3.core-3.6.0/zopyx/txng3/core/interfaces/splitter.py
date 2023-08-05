###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

from zope.interface import Interface

class ISplitter(Interface):
    """ interface class for TextIndexNG3 splitters """


    def split(some_string):
        """ splits a unicode 'some_string' string into a sequence of unicode
            strings.
        """
