# *-* coding: iso-8859-15 *-*

from pyparsing import*

class BaseNode(object):
    
    def __str__(self):
        return '%s' % (self.__class__.__name__)


class TermNode(BaseNode):

    def __init__(self, term):
        self.term = term

    def __str__(self):
        return '%s("%s")' % (self.__class__.__name__, self.term)
    __repr__ = __str__


class TermTruncLeftNode(TermNode):
    pass

class TermTruncRightNode(TermNode):
    pass

class TermSimiliarNode(TermNode):
    pass

class TermRegexNode(TermNode):
    pass

class TermSubstringNode(TermNode):
    pass


class AndNode(BaseNode):
    def __init__(self, tokens):
        self.tokens = tokens

    def __str__(self):
        return '%s("%s")' % (self.__class__.__name__, ' '.join([repr(t) for t in self.tokens]))
    __repr__ = __str__

class OrNode(AndNode):
    pass

class PhraseNode(AndNode):
    pass
    

import re

Term = Regex(r'\w+' , re.UNICODE)
Term.setParseAction(lambda s, loc, toks: TermNode(toks[0]))

TermTruncRight = Regex(r'\w+' + '\*', re.UNICODE)
TermTruncRight.setParseAction(lambda s, loc, toks: TermTruncRightNode(toks[0][:-1]))

TermTruncLeft = Regex(r'\*' + r'\w+' , re.UNICODE)
TermTruncLeft.setParseAction(lambda s, loc, toks: TermTruncLeftNode(toks[0][1:]))

TermSubstring = Regex('\*' + r'\w+' + '\*', re.UNICODE)
TermSubstring.setParseAction(lambda s, loc, toks: TermSubstringNode(toks[0][1:-1]))

TermSimiliar = Regex(r'\%' + r'\w*' , re.UNICODE)
TermSimiliar.setParseAction(lambda s, loc, toks: TermSimiliarNode(toks[0][1:]))

TermRegex= Regex(r'\w[\w\*\?]+\w' , re.UNICODE)
TermRegex.setParseAction(lambda s, loc, toks: TermRegexNode(toks[0][1:]))


PLeft = Word('(')
PRight = Word(')')
Quote = Word('"')


ListOfTerms = OneOrMore(Or([Term, TermSimiliar, TermTruncLeft, TermTruncRight, TermRegex, TermSubstring]))

AndList = Word('AND') + PLeft + ListOfTerms + PRight
AndList.setParseAction(lambda s, loc, toks: AndNode(toks[2:-1]))

OrList = Word('OR') + PLeft + ListOfTerms + PRight
OrList.setParseAction(lambda s, loc, toks: OrNode(toks[2:-1]))

Phrase = Quote + OneOrMore(Term) + Quote
Phrase.setParseAction(lambda s, loc, toks: PhraseNode(toks[1:-1]))

#root = Or([ListOfTerms, Phrase, AndList,OrList] )
root = ListOfTerms ^ Phrase ^  AndList ^ OrList
#root.setDebug(True)



for query in ('The quick *brown* fox reg*x foo?xx*regex', '"This is my phrase"', 'Something mix* *ed %foo', 'vögel und ärger', 'AND(foo bar)', 'OR(foo* *b)'):
    query = unicode(query, 'iso-8859-15')
    print '-'*80
    print repr(query)
    print root.parseString(query)
