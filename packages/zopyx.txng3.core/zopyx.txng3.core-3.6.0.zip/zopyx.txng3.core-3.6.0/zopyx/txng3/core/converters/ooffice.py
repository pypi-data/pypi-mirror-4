###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

""" 
a simple OpenOffice converter 

$Id: ooffice.py 2055 2009-03-14 10:13:45Z ajung $
"""

import xml.sax
import zipfile, cStringIO
from xml.sax.handler import ContentHandler

from zopyx.txng3.core.baseconverter import BaseConverter


class ootextHandler(ContentHandler):

    def characters(self, ch):
        self._data.write(ch.encode("utf-8") + ' ')

    def startDocument(self):
        self._data = cStringIO.StringIO()

    def getxmlcontent(self, doc):

        file = cStringIO.StringIO(doc)

        doctype = """<!DOCTYPE office:document-content PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "office.dtd">"""
        xmlstr = zipfile.ZipFile(file).read('content.xml')
        xmlstr = xmlstr.replace(doctype,'')       
        return xmlstr

    def getData(self):
        return self._data.getvalue()


class Converter(BaseConverter):

    content_type = ('application/vnd.sun.xml.calc',
          'application/vnd.sun.xml.calc.template',
          'application/vnd.sun.xml.draw',
          'application/vnd.sun.xml.draw.template',
          'application/vnd.sun.xml.impress',
          'application/vnd.sun.xml.impress.template',
          'application/vnd.sun.xml.math',
          'application/vnd.sun.xml.writer',
          'application/vnd.sun.xml.writer.global',
          'application/vnd.sun.xml.writer.template',
          'application/vnd.oasis.opendocument.chart',
          'application/vnd.oasis.opendocument.database',
          'application/vnd.oasis.opendocument.formula',
          'application/vnd.oasis.opendocument.graphics',
          'application/vnd.oasis.opendocument.graphics-template otg',
          'application/vnd.oasis.opendocument.image',
          'application/vnd.oasis.opendocument.presentation',
          'application/vnd.oasis.opendocument.presentation-template otp',
          'application/vnd.oasis.opendocument.spreadsheet',
          'application/vnd.oasis.opendocument.spreadsheet-template ots',
          'application/vnd.oasis.opendocument.text',
          'application/vnd.oasis.opendocument.text-master',
          'application/vnd.oasis.opendocument.text-template ott',
          'application/vnd.oasis.opendocument.text-web')
    
    content_description = "OpenOffice, all formats"

    def convert(self, doc, encoding, mimetype,
                logError=False, raiseException=False):
        handler = ootextHandler()
        xmlstr = handler.getxmlcontent(doc)
        xml.sax.parseString(xmlstr, handler)
        return handler.getData(), 'utf-8'

OOfficeConverter = Converter()
