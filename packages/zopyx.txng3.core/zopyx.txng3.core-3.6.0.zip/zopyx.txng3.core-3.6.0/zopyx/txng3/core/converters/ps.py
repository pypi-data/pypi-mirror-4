###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
Postscript converter

$Id: ps.py 2055 2009-03-14 10:13:45Z ajung $
"""

from zopyx.txng3.core.baseconverter import BaseConverter

class Converter(BaseConverter):

    content_type = ('application/postscript',)
    content_description = "Adobe Postscript Document"
    depends_on = 'ps2ascii'

    def convert(self, doc, encoding, mimetype,
                logError=False, raiseException=False):
        tmp_name = self.saveFile(doc)
        return self.execute('ps2ascii "%s" -' % tmp_name), 'iso-8859-15'

PSConverter = Converter()
