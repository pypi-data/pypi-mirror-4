###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
pdf converter

$Id: pdf.py 2055 2009-03-14 10:13:45Z ajung $
"""

from zopyx.txng3.core.baseconverter import BaseConverter

class Converter(BaseConverter):

    content_type = ('application/pdf',)
    content_description = "Adobe Acrobat PDF"
    depends_on = 'pdftotext'

    def convert(self, doc, encoding, mimetype,
                logError=False, raiseException=False):
        """Convert pdf data to raw text"""
        tmp_name = self.saveFile(doc)
        return self.execute('pdftotext -enc UTF-8 "%s" -' % tmp_name), 'utf-8'

PDFConverter = Converter()
