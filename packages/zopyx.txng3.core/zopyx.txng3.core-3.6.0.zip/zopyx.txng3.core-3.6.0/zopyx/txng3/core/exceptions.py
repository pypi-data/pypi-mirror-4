###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
Exception used throughout TextIndexNG

$Id: exceptions.py 2054 2009-03-14 10:11:29Z ajung $
"""

from zope.interface import implements
from zopyx.txng3.core.interfaces.converter import IConversionError

class BaseConverterError(Exception): pass
class LexiconError(Exception): pass
class NormalizerError(Exception): pass
class StopwordError(Exception): pass
class StorageException(Exception): pass

class ConversionError(Exception):
    implements(IConversionError)