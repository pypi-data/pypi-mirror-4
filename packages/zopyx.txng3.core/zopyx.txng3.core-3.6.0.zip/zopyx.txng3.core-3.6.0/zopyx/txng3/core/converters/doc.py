###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
WinWord converter

$Id: doc.py 2055 2009-03-14 10:13:45Z ajung $
"""

import os, sys

from zopyx.txng3.core.exceptions import ConversionError
from zopyx.txng3.core.baseconverter import BaseConverter
from zopyx.txng3.core.baseconverter import TmpFile
from zopyx.txng3.core.logger import LOG

try:
    from App.Common import package_home
    wvConf_file = os.path.join(package_home(globals()), 'wvText.xml')
except ImportError:
    wvConf_file = os.path.join(os.path.dirname(__file__), 'wvText.xml')


class Converter(BaseConverter):

    content_type = ('application/msword',
                    'application/ms-word',
                    'application/vnd.ms-word')
    content_description = "Microsoft Word 2000, 97, 95, 6"
    depends_on = 'wvWare'

    def convert(self, doc, encoding, mimetype,
                logError=False, raiseException=False):
        """Convert WinWord document to raw text"""
        
        tmp_name = self.saveFile(doc)
        err = TmpFile('')
        if sys.platform == 'win32':
            result = (self.execute(
                '%s -c utf-8 --nographics -x "%s" "%s" 2> "%s"' % (
                    self.depends_on, wvConf_file, tmp_name, str(err))), 'utf-8')
        else:
            result = (self.execute(
                '%s -c utf-8 --nographics -x "%s" "%s" 2> "%s"' % (
                    self.depends_on, wvConf_file, tmp_name, str(err))), 'utf-8')
        
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

DocConverter = Converter()
