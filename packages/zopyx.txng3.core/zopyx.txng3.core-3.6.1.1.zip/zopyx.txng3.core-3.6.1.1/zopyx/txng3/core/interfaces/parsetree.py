###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

""" interface for ParseTree nodes """

from zope.interface import Interface

class IParseTreeNode(Interface):
    """ interface class for ParseTreeNode """

    def getType():  
        """ return type of node """

    def getValue():
        """ return value of node """

    def setValue(value):
        """ set the value of a node """

    def getField():
        """ return the field value for the node """            
