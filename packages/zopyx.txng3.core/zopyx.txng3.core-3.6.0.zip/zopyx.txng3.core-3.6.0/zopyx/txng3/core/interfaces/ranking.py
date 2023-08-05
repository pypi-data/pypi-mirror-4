###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

import zope.interface
import zopyx.txng3.core.config


class IRanking(zope.interface.Interface):

    def __call__(index, resultset,
                 language=zopyx.txng3.core.config.DEFAULT_LANGUAGE,
                 max=50):
        """Rank given result set.

        return sequence of tuples (result, score)
        XXX specify score

        """
