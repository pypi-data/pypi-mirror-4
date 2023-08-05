###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################


from zope.interface import implements
from zopyx.txng3.core.interfaces import IParser 

from english import EnglishParser

class GermanParser:

    implements(IParser)

    def __init__(self, language='de'):
        self._parser = EnglishParser(language)
        self.map = {
            'und' : 'AND',
            'oder' : 'OR',
            'nahe' : 'NEAR',
            'nicht' : 'NOT',
            }
        self.map_keys = self.map.keys()

    def getLanguage(self):
        return self._parser.getLanguage()


    def parse(self, query):
        words = query.split(' ')

        lst = []
        inside_quotes = False
        for w in words:

            if '"' in w:
                if inside_quotes:
                    inside_quotes = False
                else:
                    inside_quotes = True

            if not inside_quotes:
                if w.lower() in self.map_keys:
                    w = self.map[w.lower()]
                elif '::' in w:

                    for  k,v in self.map.items():
                        x = '::' + k
                        if x.lower() in w.lower():
                            w = w.replace(x, '::' + v)
                            w = w.replace(x.upper(), '::' + v)
                            break

            lst.append(w)

        query = ' '.join(lst)
        return self._parser.parse(query)
        

if __name__ == '__main__':
    parser = GermanParser()
    print parser.parse('a und b')
    print parser.parse('a und "foo und bar"')
    print parser.parse('a und b oder (c and d)')
    print parser.parse('somefield::UND(a b c)')


GermanQueryParser = GermanParser()
