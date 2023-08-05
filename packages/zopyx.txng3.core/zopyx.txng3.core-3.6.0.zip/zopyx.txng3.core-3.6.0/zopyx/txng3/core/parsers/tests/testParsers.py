###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

import sys, unittest

from zope.component import getUtility
from zope.interface.verify import verifyClass

from zopyx.txng3.core.interfaces.parser import IParser
from zopyx.txng3.core.parsetree import WordNode, TruncNode, GlobNode, SimNode, LTruncNode
from zopyx.txng3.core.parsetree import AndNode, PhraseNode, NearNode, OrNode, NotNode, SubstringNode, RangeNode

from zopyx.txng3.core.parsers.english import EnglishParser, QueryParserError
from zopyx.txng3.core.parsers.german import GermanParser
from zopyx.txng3.core.parsers.french import FrenchParser
from zopyx.txng3.core.parsers.dumb import DumbOrParser, DumbAndParser

def flatten(node, lst=[]):
    lst.append(repr(node))
    try:
        for n in node.getValue():
            flatten(n, lst)
    except:
        pass
    return lst


class EnglishParserTests(unittest.TestCase):

    def setUp(self):

        self.p = EnglishParser()
        self.d = {'and' : 'and', 'or' : 'or', 'near' : 'near', 'not' : 'not',
                  'AND' : 'AND', 'OR' : 'OR', 'NEAR' : 'NEAR', 'NOT' : 'NOT'}

    def testInterface(self):
        verifyClass(IParser, self.p.__class__)

    def _test(self, query, expected):
        query = query % self.d
        got = self.p.parse(query)
        got_lst = []
        flatten(got, got_lst)
        expected_lst = []
        flatten(expected, expected_lst)
        if expected_lst != got_lst:
            raise AssertionError('\nParser: %s\nquery: %s\ngot:      %s\nexpected: %s\nlexer: %s' % (self.p.__class__.__name__, query, got, expected, self.p.lexer(query)))
    
    def testEmpty(self):
        self._test(u'' , None)

    def testSimple(self):
        self._test(u'a' ,   WordNode(u'a'))
        self._test(u'1' ,   WordNode(u'1'))
        self._test(u'foo' , WordNode(u'foo'))
        self._test(u'123' , WordNode(u'123'))

    def testWithSeparators(self):
        self._test(u'a' ,   WordNode(u'a'))
        self._test(u'1' ,   WordNode(u'1'))
        self._test(u'foo' , WordNode(u'foo'))
        self._test(u'C++' , WordNode(u'C++'))

    def testGlobbing(self):
        self._test(u'foo*',   TruncNode(u"foo"))
        self._test(u'*foo',   LTruncNode(u"foo"))
        self._test(u'%%foo',   SimNode(u"foo"))
        self._test(u'fo?o*',  GlobNode(u"fo?o*"))
        self._test(u'?fo?o*', GlobNode(u"?fo?o*"))
        self._test(u'*foo*',  SubstringNode(u"foo"))
        self._test(u'bar..foo',  RangeNode((u'bar',u'foo')))

    def testAnd(self):
        self._test(u'foo %(and)s bar', 
            AndNode((WordNode(u"foo"),WordNode(u"bar"))) )
        self._test(u'foo %(and)s bar', 
            AndNode((WordNode(u"foo"),WordNode(u"bar"))))
        self._test(u'foo %(and)s bar %(and)s sux', 
            AndNode(((WordNode(u"foo"),AndNode((WordNode(u"bar"),WordNode(u"sux")))))))
        self._test(u'C++ %(and)s Algol68' , 
            AndNode((WordNode(u'C++'),WordNode(u"Algol68"))))
        self._test('somefield::%(and)s(a b c)',
            AndNode((WordNode("a"),WordNode('b'), WordNode('c')), 'somefield'))
        self._test('somefield::%(and)s(a *b c*)',
            AndNode((WordNode("a"),LTruncNode('b'), TruncNode('c')), 'somefield'))
        
    def testOR(self):
        self._test('foo %(or)s bar', 
            OrNode((WordNode("foo"),WordNode("bar"))))
        self._test('foo %(OR)s bar', 
            OrNode((WordNode("foo"),WordNode("bar"))))
        self._test('foo %(or)s  bar %(OR)s sux', 
            OrNode((WordNode("foo"),OrNode((WordNode("bar"),WordNode("sux"))))))
        self._test('somefield::%(or)s(a b c)',
            OrNode((WordNode("a"),WordNode('b'), WordNode('c')), 'somefield'))
        self._test('somefield::%(or)s(a b c)',
            OrNode((WordNode("a"),WordNode('b'), WordNode('c')), 'somefield'))
        self._test('some_field1::%(or)s(a *b c*)',
            OrNode((WordNode("a"), LTruncNode('b'), TruncNode('c')), 'some_field1'))
        self._test('default::%(or)s(a b c)',
            OrNode((WordNode("a"),WordNode('b'), WordNode('c'))))

    def testNear(self):
        self._test('foo %(near)s bar',   
            NearNode((WordNode("foo"),WordNode("bar"))))
        self._test('foo %(NEAR)s bar', 
            NearNode((WordNode("foo"),WordNode("bar"))))
        self._test('somefield::near(a b c)',
            NearNode((WordNode("a"),WordNode("b"),WordNode("c")), 'somefield'))

    def testPhrase(self):
        self._test('"foo"', 
            PhraseNode((WordNode("foo"),)))
        self._test('"foo bar"', 
            PhraseNode((WordNode("foo"),WordNode("bar"))))
        self._test('"foo bar sucks"' , 
            PhraseNode((WordNode("foo"),WordNode("bar"),WordNode("sucks"))))
        self._test('"bar %(or)s foo"' , 
            PhraseNode((WordNode("bar"),WordNode('%(or)s' % self.d),WordNode("foo"))))
        self._test('"bar %(near)s foo"' , 
            PhraseNode((WordNode("bar"),WordNode('%(near)s' % self.d),WordNode("foo"))))
        self._test('"bar %(not)s foo"' , 
            PhraseNode((WordNode("bar"),WordNode('%(not)s' % self.d),WordNode("foo"))))
        self._test('"bar %(and)s %(not)s foo"' , 
            PhraseNode((WordNode("bar"),WordNode('%(and)s' % self.d), WordNode('%(not)s' % self.d),WordNode("foo"))))
        self._test('somefield::PHRASE(foo bar sucks)' , 
            PhraseNode((WordNode("foo"),WordNode("bar"),WordNode("sucks")), 'somefield'))
        self._test('somefield::phrase( foo bar sucks)' , 
            PhraseNode((WordNode("foo"),WordNode("bar"),WordNode("sucks")), 'somefield'))

    def testNot(self):
        self._test('%(NOT)s  bar',
            NotNode(WordNode('bar')))
        self._test('%(NOT)s - bar',
            NotNode(NotNode(WordNode('bar'))))
        self._test('language-code',
            WordNode('language-code'))
        self._test('- bar',
            NotNode(WordNode('bar')))
        self._test('foo %(and)s %(not)s bar',
            AndNode((WordNode('foo'),NotNode(WordNode('bar')))))
        self._test('foo %(and)s -bar',
            AndNode((WordNode('foo'),NotNode(WordNode('bar')))))
        self._test('not (a and b)',
            NotNode(AndNode((WordNode('a'), WordNode('b')))))
        self._test('not a and b',
            AndNode((NotNode(WordNode('a')), WordNode('b'))))
        self._test('-a and b',
            AndNode((NotNode(WordNode('a')), WordNode('b'))))

    def testBastardQueries(self):
        self._test('andhausen %(or)s oriole',
            OrNode((WordNode('andhausen'), WordNode('oriole'))))
        self._test('and %(or)s or',
            OrNode((WordNode('and'), WordNode('or'))))
        self._test('("here")',
            PhraseNode((WordNode('here'), )))

    def testFieldsSimple(self):
        self._test('somefield::foo', WordNode('foo', 'somefield'))
        self.assertRaises(QueryParserError, self._test, 'somefield : foo', WordNode('somefield', 'foo'))

    def testStupidPlone(self):
        self._test('"("foo")"', WordNode('foo'))
        


class GermanParserTests(EnglishParserTests):

    def setUp(self):
        self.p = GermanParser()
        self.d = {'and' : 'und', 'or' : 'oder', 'near' : 'nahe', 'not' : 'nicht',
                  'AND' : 'und', 'OR' : 'ODER', 'NEAR' : 'NAHE', 'NOT' : 'NICHT'}

class FrenchParserTests(EnglishParserTests):

    def setUp(self):
        self.p = FrenchParser()
        self.d = {'and' : 'et', 'or' : 'ou', 'near' : 'pres', 'not' : 'sauf',
                  'AND' : 'ET', 'OR' : 'OU', 'NEAR' : 'PRES', 'NOT' : 'SAUF'}


class DumbTestBase(unittest.TestCase):

    def _test(self, query, expected):
        got = self.p.parse(query)
        got_lst = []
        flatten(got, got_lst)
        expected_lst = []
        flatten(expected, expected_lst)
        if expected_lst != got_lst:
            raise AssertionError('\nParser: %s\nquery: %s\ngot:      %s\nexpected: %s' % (self.p.__class__.__name__, query, got, expected))


class DumbOrTests(DumbTestBase):

    def setUp(self):
        self.p = DumbOrParser()

    def testInterface(self):
        verifyClass(IParser, DumbOrParser)


    def testOr(self):
        self._test('a b c', OrNode((WordNode("a"),WordNode("b"), WordNode('c'))))
        self._test('a foo', OrNode((WordNode("a"),WordNode("foo"))))
        self._test('', None)
        
class DumbAndTests(DumbTestBase):

    def setUp(self):
        self.p = DumbAndParser()

    def testInterface(self):
        verifyClass(IParser, DumbAndParser)

    def testAnd(self):
        self._test('a b c', AndNode((WordNode("a"),WordNode("b"), WordNode('c'))))
        self._test('a foo', AndNode((WordNode("a"),WordNode("foo"))))
        self._test('', None)

def test_suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(EnglishParserTests))
    s.addTest(unittest.makeSuite(GermanParserTests))
    s.addTest(unittest.makeSuite(FrenchParserTests))
    s.addTest(unittest.makeSuite(DumbOrTests))
    s.addTest(unittest.makeSuite(DumbAndTests))
    return s

def main():
   unittest.TextTestRunner().run(test_suite())

def debug():
   test_suite().debug()

def pdebug():
    import pdb
    pdb.run('debug()')
   
if __name__=='__main__':
   if len(sys.argv) > 1:
      globals()[sys.argv[1]]()
   else:
      main()

