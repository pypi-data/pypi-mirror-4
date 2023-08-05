###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
A stupid HTML to Ascii converter

$Id: sgml.py 2055 2009-03-14 10:13:45Z ajung $
"""

import re
import sys
from zopyx.txng3.core.baseconverter import BaseConverter
from StripTagParser import StripTagParser
from entities import convert_entities

default_encoding = sys.getdefaultencoding()
encoding_reg = re.compile('encoding="(.*?)"')

class Converter(BaseConverter):

    content_type = ('text/sgml', 'text/xml')
    content_description = "SGML, XML"

    def convert(self, doc):
        """Convert html data to raw text"""

        p = StripTagParser()
        p.feed(doc)
        p.close()
        return str(p)

    def convert(self, doc, encoding, mimetype,
                logError=False, raiseException=False):

        # Use encoding from XML preamble if present
        mo = encoding_reg.search(doc)
        if mo:
            encoding = mo.group(1)

        if not encoding:
            encoding = default_encoding
        
        if not isinstance(doc, unicode):
            doc = unicode(doc, encoding, 'replace')
        doc = convert_entities(doc)
        doc = doc.encode('utf-8')
        p = StripTagParser()
        p.feed(doc)
        p.close()
        return str(p), 'utf-8'

SGMLConverter = Converter()
