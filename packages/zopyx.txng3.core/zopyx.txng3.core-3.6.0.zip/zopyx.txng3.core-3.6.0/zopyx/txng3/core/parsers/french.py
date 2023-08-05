###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################


from german import GermanParser

class FrenchParser(GermanParser):

    def __init__(self):
        self._parser = GermanParser('fr')
        self.map = {
                'et' : 'AND',
                'ou' : 'OR',
                'pres' : 'NEAR',
                'sauf' : 'NOT',
            }

        self.map_keys = self.map.keys()


if __name__ == '__main__':
    parser = FrenchParser()
    print parser.parse('a et b')
    print parser.parse('a et "foo ou bar"')
    print parser.parse('a et b ou (c et d)')
    print parser.parse('somefield::ou(a b c)')


FrenchQueryParser = FrenchParser()
