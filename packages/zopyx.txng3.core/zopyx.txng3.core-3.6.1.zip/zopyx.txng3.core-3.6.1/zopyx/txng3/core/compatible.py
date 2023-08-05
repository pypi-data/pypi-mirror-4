###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

# Zope 2 - Zope 3 compability imports


try:
    from Persistence import Persistent 
except ImportError:
    from persistent import Persistent    


try:
    from Products.PluginIndexes.common import safe_callable as callable
except ImportError:
    callable = callable
