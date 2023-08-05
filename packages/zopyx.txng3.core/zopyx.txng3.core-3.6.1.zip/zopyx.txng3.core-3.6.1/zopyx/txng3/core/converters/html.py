###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
a stupid HTML to Ascii converter

$Id: html.py 2055 2009-03-14 10:13:45Z ajung $
"""

import re
from zopyx.txng3.core.baseconverter import BaseConverter
from entities import convert_entities
from stripogram import html2text

charset_reg = re.compile('text/html.*?charset=(.*?)"', re.I|re.M)

class Converter(BaseConverter):

    content_type = ('text/html',)
    content_description = "HTML"

    def convert(self, doc, encoding=None, mimetype=None,
                logError=False, raiseException=False):

        # convert to unicode
        if not isinstance(doc, unicode):
            if not encoding:
                mo = charset_reg.search(doc)
                if mo is not None:
                    encoding = mo.group(1)
                else:
                    encoding = 'ascii' # guess
            doc = unicode(doc, encoding, 'replace')
        doc = convert_entities(doc)
        result = html2text(doc)

        # convert back to utf-8
        return result.encode('utf-8'), 'utf-8'

HTMLConverter = Converter()
