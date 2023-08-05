###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################


try:
    from zLOG import INFO, ERROR, WARNING, BLATHER
    from zLOG import LOG as zLOG
    have_z2 = True
except:
    import logging 
    have_z2 = False

ident = 'txng'


def PyLogger():
    """ A standard Python logger """

    from config import LOGGER_FILE

    logger = logging.getLogger('textindexng3')
    hdlr = logging.FileHandler(LOGGER_FILE)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr) 
    logger.setLevel(logging.DEBUG)
    return logger


class Z2Logger:
    """ Logger using zLOG """
    
    def debug(self, text, exc_info=None):
        zLOG(ident, BLATHER, text, error=exc_info)

    def info(self, text, exc_info=None):
        zLOG(ident, INFO, text, error=exc_info)

    def warn(self, text, exc_info=None):
        zLOG(ident, WARNING, text, error=exc_info)

    def error(self, text, exc_info=None):
        zLOG(ident, ERROR, text, error=exc_info)

    def __call__(self, text):
        self.info(text)

def Logger():
    """ Logger factory """
    
    if have_z2:
        return Z2Logger()
    else:
        return PyLogger()        


LOG = Logger()
