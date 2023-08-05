###########################################################################
# TextIndexNG V 3
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

from zope.interface import Interface
import zopyx.txng3.core.config


class IResultSet(Interface):
    """ interface for result sets """

    def getWords():
        """ return a list of words being involved in a particular
            subquery.
        """

    def getDocids():
        """ return a DocidList instance representing all matching
            document ids from a particular subquery
        """

    def ranking(ranking_function,
                index,
                language=zopyx.txng3.core.config.DEFAULT_LANGUAGE,
                nbest=50):
        """ Apply the ranking_function (IRanking) to the result set and keep
            the 'nbest' hits (highest score).

        """

    def getRankedResults():
        """ Return a sorted sequence of tuple (docid, score). A resultset
            must be ranked before by calling cosine_ranking(). Calling this
            method on a unranked result set, it will return None.
        """
