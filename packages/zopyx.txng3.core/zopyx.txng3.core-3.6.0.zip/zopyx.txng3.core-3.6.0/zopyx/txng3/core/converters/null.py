###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
a stupid null converter

$Id: null.py 2055 2009-03-14 10:13:45Z ajung $
"""

from zopyx.txng3.core.baseconverter import BaseConverter

class Converter(BaseConverter):

    content_type = ('text/plain',)
    content_description = "Plain text"

    def convert(self, doc, encoding, mimetype,
                logError=False, raiseException=False):
        return doc, encoding

NullConverter = Converter()
