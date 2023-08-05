###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

import os
import subprocess
import tempfile

from zope.interface import implements
from zopyx.txng3.core.interfaces import IConverter
from zopyx.txng3.core.exceptions import BaseConverterError


class TmpFile:

    def __init__(self, data):
        self.fname = tempfile.mktemp()
        out = open(self.fname,'w+b')
        if isinstance(data, str):
            out.write(data)
            out.flush()
            return
        from ZPublisher.Iterators import IStreamIterator
        if IStreamIterator.isImplementedBy(data):
            for block in data:
                out.write(block)
                block._p_deactivate()
            out.flush()
        else:
            raise ValueError("Don't know how to write data!")

    def __str__(self): return self.fname
    __repr__ = __str__

    def __del__(self):
        os.unlink(self.fname)


def findOnWin32Path(fname):
    lookat = os.getenv("PATH", '').split(';')
    executables = os.getenv("PATHEXT", '.EXE;.COM;.BAT;.CMD').split(';')
    for dir in lookat:
        if os.path.exists(os.path.join(dir,fname)):
            return True
        for exe in executables:
            if os.path.exists(os.path.join(dir,fname+exe)):
                return True
    return False


class BaseConverter(object):
    """ Base class for all converters """

    content_type = None
    content_description = None

    implements(IConverter)

    def __init__(self):
        if not self.content_type:
            raise BaseConverterError('content_type undefinied')

        if not self.content_description:
            raise BaseConverterError('content_description undefinied')

    def execute(self, com):
        try:
            import win32pipe
            return win32pipe.popen(com).read()
        except ImportError:
            return os.popen(com).read()

    def saveFile(self, data):
        return TmpFile(data)

    def getDescription(self):   
        return self.content_description

    def getType(self):          
        return self.content_type

    def getDependency(self):    
        return getattr(self, 'depends_on', None)

    def __call__(self, s):      
        return self.convert(s)
   
    def isAvailable(self):
        depends_on = self.getDependency()
        if depends_on:
            if os.name == 'posix':
                out = subprocess.Popen(['which', depends_on],
                                       stdout=subprocess.PIPE).communicate()[0]
                if out.find('no %s' % depends_on) > - 1 or out.lower().find('not found') > -1 or len(out.strip()) == 0:
                    return 'no'
                return 'yes'
            elif os.name == 'nt':
                if findOnWin32Path(depends_on):
                    return 'yes'
                else:
                    return 'no'
            else:
                return 'unknown'
        else:
            return 'always'
