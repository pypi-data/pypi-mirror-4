###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
Excel Converter

$Id: xls.py 2055 2009-03-14 10:13:45Z ajung $
"""

import sys
from zopyx.txng3.core.exceptions import ConversionError
from zopyx.txng3.core.baseconverter import BaseConverter
from zopyx.txng3.core.baseconverter import TmpFile
from zopyx.txng3.core.logger import LOG

class Converter(BaseConverter):

    content_type = ('application/msexcel',
                    'application/ms-excel',
                    'application/vnd.ms-excel')
    content_description = "Microsoft Excel"
    depends_on = 'xls2csv'

    def convert(self, doc, encoding, mimetype,
                logError=False, raiseException=False):
        """Convert Excel document to raw text"""

        tmp_name = self.saveFile(doc)
        err = TmpFile('')

        if sys.platform == 'win32':
            result = (self.execute('xls2csv /d 8859-1 /q 0 "%s" 2> %s' % (
                tmp_name, str(err))), 'iso-8859-15')
        else:
            result = (self.execute('xls2csv -d 8859-1 -q 0 "%s" 2> %s' % (
                tmp_name, str(err))), 'iso-8859-15')
        
        try:
            errors = open(str(err), 'r+').read()
        except OSError:
            errors = ""
        if errors:
            if logError:
                LOG.warn('Converter %s experienced an error %s' % (
                    self.content_description, errors)
                )
            if raiseException:
                raise ConversionError(errors)
        
        return result

XLSConverter = Converter()
