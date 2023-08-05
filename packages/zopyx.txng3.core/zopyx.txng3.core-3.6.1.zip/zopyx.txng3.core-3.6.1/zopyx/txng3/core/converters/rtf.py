###########################################################################
#
# TextIndexNG                The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
###########################################################################

""" 
a simple RTF converter

$Id: rtf.py 2055 2009-03-14 10:13:45Z ajung $
"""

import os
import sys
import xml.sax
import cStringIO
import tempfile
from xml.sax.handler import ContentHandler

from zopyx.txng3.core.baseconverter import BaseConverter, findOnWin32Path

class RTFtextHandler(ContentHandler):

    def characters(self, ch):
        self._data.write(ch.encode("UTF-8") + ' ')

    def startDocument(self):
        self._data = cStringIO.StringIO()

    def getData(self):
        return self._data.getvalue()


class Converter(BaseConverter):

    content_type = ('application/rtf','text/rtf')
    content_description = "RTF"
    depends_on = 'rtf2xml'
    
    def __init__(self):
        BaseConverter.__init__(self)
        
        if sys.platform == 'win32':
            self._rtf2xml = findOnWin32Path(self.depends_on)

    def convert(self, doc, encoding, mimetype,
                logError=False, raiseException=False):
        """ convert RTF Document """
        tmp_name = self.saveFile(doc)

        if sys.platform == 'win32':
            tempdir = os.getenv("TEMP", os.getenv("TMP", ''))
            tempbat = tempfile.mktemp(suffix='.bat', prefix='temp_converter_')
            
            open(tempbat,'w+').write('cd /d "%s"\n%s "%s" --no-dtd "%s"' % (
                tempdir, sys.executable, self._rtf2xml, tmp_name))
            
            try:
                xmlstr = self.execute(tempbat)
            finally:
                os.remove(tempbat)
        else:
            xmlstr = self.execute('cd /tmp && rtf2xml --no-dtd "%s"' % tmp_name)
        
        handler = RTFtextHandler()
        xml.sax.parseString(xmlstr, handler)
        return handler.getData(), 'utf-8'

    def convert2(self, doc, encoding, mimetype):
        return self.convert(doc), 'utf-8'

RTFConverter = Converter()
