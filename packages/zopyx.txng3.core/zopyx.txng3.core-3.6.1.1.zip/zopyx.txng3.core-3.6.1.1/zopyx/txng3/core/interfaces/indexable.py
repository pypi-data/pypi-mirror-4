###########################################################################
# TextIndexNG V 3
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
indexable interfaces

$Id: indexable.py 1751 2007-01-23 15:26:42Z yvoschu $
"""

from zope.interface import Interface


class IIndexContentCollector(Interface):
    """ Defines an API for a helper class to pass indexable content from
        objects to the index.
    """

    def addContent(field, text, language=None):
        """ Add unicode string 'text' as indexable content for 'field'.
            'language' specifies the language if available.
        """

    def addBinary(field, data, mimetype, encoding=None, language=None):
        """ Add some binary 'data' that needs to be converted as indexable 
            content for 'field'. 
        """

    def getFields():
        """ return a list of index fields """

    def getFieldData(field):
        """Get indexed data for a particular field.

        Returns a sequence of dictionaries.
        """


class IIndexableContent(Interface):

    def indexableContent(fields):
        """ returns an instance implementing IIndexContentCollector """
