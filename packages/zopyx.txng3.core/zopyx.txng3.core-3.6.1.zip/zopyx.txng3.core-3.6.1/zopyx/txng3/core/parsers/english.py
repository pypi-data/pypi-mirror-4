###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
English query parser

$Id: english.py 2377 2012-11-21 14:00:46Z ajung $
"""

import sys, re, os, tempfile
from threading import Lock

from zope.interface import implements
from zopyx.txng3.core.interfaces import IParser 
from zopyx.txng3.core.parsetree import * 
import lex, yacc

# For UNIX: create a directory /tmp/textindexng3-uid-<uid>
# For Windows: use the default tmp directory

tempdir = tempfile.gettempdir()
if os.name == 'posix':
    tempdir = os.path.join(tempfile.tempdir, 'textindexng3-uid-%d-pid-%d' % (os.getuid(), os.getpid())
    if not os.path.exists(tempdir):
        os.makedirs(tempdir, 0777)

outputdir = tempfile.mkdtemp(dir=tempdir)
if not outputdir in sys.path:
    sys.path.append(outputdir)

class QueryParserError(Exception): pass

class ParserBase:
    """ Base class for all parsers """

    tokens = ()
    precedence = ()
    names = {}

    implements(IParser)

    def __init__(self, language='en'):
        self.language = language
        self.lock = Lock()

        try:
            modname = os.path.split(os.path.splitext(__file__)[0])[1] + "_" + self.__class__.__name__
        except:
            modname = "parser"+"_"+self.__class__.__name__
        self.debugfile = modname + ".dbg"
        self.tabmodule = modname + "_" + "parsetab"

        lex.lex(module=self, debug=False)
        self.p = yacc.yacc(module=self,
                           debug=0,
                           outputdir=outputdir,
                           debugfile=self.debugfile,
                           tabmodule=self.tabmodule,)

    def getLanguage(self):
        return self.language

    def __call__(self, query):
        return self.parse(query)

    def parse(self, query):
        
        try:
            query = query.strip()
            # Plone workaround: queryCatalog.py inserts extra
            # quoting for parentheses
            query = query.replace('"("', '(')
            query = query.replace('")"', ')')

            if not query: 
                return None
            self.lock.acquire()
            self._clear()
            result = self.p.parse(query)
            self.lock.release()
            return result

        except:
            self.lock.release()
#            import traceback
#            traceback.print_exc()
            raise QueryParserError('Unable to parse query: %s' % query)


    def lexer(self, data):
        """ helper method to control lexer process. Return the tokenize
            data string.
        """

        lex.input(data)
        tokens = []
        while 1:
            tok = lex.token()
            if not tok: break
            tokens.append(tok)

        return tokens


class ElementCollector:
    """ wrapper class around a list to keep the nodes
        for a phrase search 
    """

    def __init__(self):
        self.clear()

    def clear(self):
        self._list = []
        self._field = None

    def addElement(self, item):
        self._list.insert(0, item)

    def setField(self, field):
        self._field = field

    def getElements(self):
        return tuple(self._list)

    def getField(self):
        return self._field



class PhraseElements(ElementCollector):

    def addElement(self, item):
        if not isinstance(item, WordNode):
            raise QueryParserError('Offending subquery in phrase found: %s.\nPhrases must contain *only* terms but not terms containing wildcards or other special query characters' % repr(item.getValue())) 
        ElementCollector.addElement(self, item)



# some regexes to distinguish between normal strings
# truncated strings and patterns

str_regex = re.compile(r'[^%*?()\s"]+$',re.LOCALE|re.UNICODE)
range_regex = re.compile(r'[^%*?()\s"]+\.\.[^%*?()\s"]+$',re.LOCALE|re.UNICODE)
sim_regex = re.compile(r'[%][^%*?()\s"]+$',re.LOCALE|re.UNICODE)
sub_regex = re.compile(r'[*][^%*?()\s"]+[*]$',re.LOCALE|re.UNICODE)
rt_regex  = re.compile(r'[^%*?()\s"]+[*]$',re.LOCALE|re.UNICODE)
lt_regex  = re.compile(r'[*][^%*?()\s"]+$',re.LOCALE|re.UNICODE)


class EnglishParser(ParserBase):

    tokens = (
        'STRING' , 
        'NOT',
        'OR', 
        'AND', 
        'NEAR',
        'NEAR_PREFIX',
        'PHRASE_PREFIX',
        'AND_PREFIX',
        'OR_PREFIX',
        'QUOTE',
        'OPENP', 
        'CLOSEP', 
        'COLON',
        
    )         

    t_QUOTE  = r'\"'                   
    t_OPENP  = r'\('           
    t_CLOSEP = r'\)'          

    t_ignore = '\t'

    def __init__(self, *args, **kw):
        ParserBase.__init__(self, *args, **kw)
        self._clear()

    def _clear(self):
        self.phrase_elements = PhraseElements()
        self.elements = ElementCollector()

    def t_COLON(self, t):
        r'\s*:\s*'
        return t

    def t_NOT(self, t):
        'NOT\s+|not\s+|\-'
        return t

    def t_AND(self, t):
        '\s+AND\s+|\s+and\s+'            
        return t

    def t_OR(self, t):
        '\s+OR\s+|\s+or\s+'
        return t

    def t_NEAR(self, t):
        '\s+NEAR\s+|\s+near\s+'
        return t

    def t_NEAR_PREFIX(self, t):
        '[\w+_]+::(NEAR|near)'
        return t

    def t_AND_PREFIX(self, t):
        '[\w+_]+::(AND|and)'
        return t

    def t_OR_PREFIX(self, t):
        '[\w+_]+::(OR|or)'
        return t

    def t_PHRASE_PREFIX(self, t):
        '[\w+_]+::(PHRASE|phrase)'
        return t
            
    def t_newline(self, t):
        r'\n+'
        t.lineno += t.value.count("\n")
        
    def t_error(self, t):
        
        if t.value[0] in [' ']:
            t.skip(1)
        else:
            raise QueryParserError,"Illegal character '%s'" % t.value[0]

    def p_expr_expr_factor3(self, t):
        """expr :  NOT expr"""
        t[0] = NotNode( t[2] )

    def p_expr_expr_factor2(self, t):
        """expr :  NOT factor """
        t[0] = NotNode( t[2] )

    def p_expr_parens(self, t):
        """expr :    OPENP expr CLOSEP """
        t[0] = t[2]

    def p_near_prefix(self, t):
        """expr : NEAR_PREFIX OPENP qterm CLOSEP """
        field,op = t[1].split('::')
        if field=='default': field = None
        t[0] = NearNode(self.phrase_elements.getElements(), field)
        self.phrase_elements.clear()

    def p_phrase_prefix(self, t):
        """expr : PHRASE_PREFIX OPENP qterm CLOSEP """
        field,op = t[1].split('::')
        if field=='default': field = None
        t[0] = PhraseNode(self.phrase_elements.getElements(), field)
        self.phrase_elements.clear()

    def p_and_prefix(self, t):
        """expr : AND_PREFIX OPENP terms CLOSEP """
        field,op = t[1].split('::')
        if field=='default': field = None
        t[0] = AndNode(self.elements.getElements(), field)
        self.elements.clear()

    def p_or_prefix(self, t):
        """expr : OR_PREFIX OPENP terms CLOSEP """
        field,op = t[1].split('::')
        if field=='default': field = None
        t[0] = OrNode(self.elements.getElements(), field)
        self.elements.clear()

    def p_expr_and(self, t):
        """expr :    expr AND expr """
        t[0] = AndNode( (t[1], t[3]) )

    def p_expr_or(self, t):
        """expr :    expr OR expr """
        t[0] = OrNode( (t[1], t[3]) )

    def p_expr_near(self, t):
        """expr :    expr NEAR expr """
        t[0] = NearNode( (t[1], t[3]) )

    def p_expr_noop(self, t):
        """expr :    expr expr"""
        t[0] = AndNode( (t[1], t[2]))

    def p_expr_expr_factor(self, t):
        """expr :  factor """
        t[0] = t[1]

    def p_factor_string(self, t):
        """factor : string"""
        t[0] = t[1]

    def p_factor_quote(self, t):
        """factor :  quotestart qterm quoteend """
        t[0] = PhraseNode(self.phrase_elements.getElements(), self.phrase_elements.getField())
        self.phrase_elements.clear()

    def p_qterm_1(self, t):
        """ qterm : string qterm"""
        self.phrase_elements.addElement(t[1])
        t[0] = [t[1], t[2]]
     
    def p_qterm_2(self, t):
        """ qterm : string"""
        self.phrase_elements.addElement(t[1]) 
        t[0] = t[1]

    def p_terms(self, t):
        """ terms : string terms"""
        self.elements.addElement(t[1])
        t[0] = [t[1], t[2]]

    def p_terms_1(self, t):
        """ terms : string"""
        self.elements.addElement(t[1]) 
        t[0] = t[1]

    def p_quotestart_1(self, t):
        """ quotestart : QUOTE """
        self.phrase_elements.clear() 
    
    def p_quotestart_with_field(self, t):
        """ quotestart : phrasefield COLON QUOTE """
        self.phrase_elements.clear() 

    def p_phrasefield(self, t):
        """ phrasefield : STRING """
        self.phrase_elements.setField(t[1])

    def p_quoteend_1(self, t):
        """ quoteend : QUOTE """

    def p_string(self, t):
        """string :  STRING
           | AND 
           | OR 
           | NEAR 
           | NOT"""

        v = t[1].strip()
        if range_regex.match(v): t[0] = RangeNode(tuple(v.split('..')) )
        elif str_regex.match(v): 

            if '::' in v:
                field, value= v.split('::')
                t[0] = WordNode(*(value, field))
            else:
                t[0] = WordNode(v)
            
        elif sim_regex.match(v): t[0] = SimNode(v[1:] )
        elif sub_regex.match(v): t[0] = SubstringNode(v[1:-1] )
        elif rt_regex.match(v):  t[0] = TruncNode(v[:-1] )
        elif lt_regex.match(v):  t[0] = LTruncNode(v[1:] )
        else:             
            if not (v.lower().strip() in ('and', 'or', 'not', 'near')):
                t[0] = GlobNode(t[1])

    def t_STRING(self, t):
        r'[^()\s"]+' 
        return t

    def p_error(self, t):
        raise QueryParserError("Syntax error at '%s'" % t.value)

        
EnglishQueryParser = EnglishParser('en')


if __name__== '__main__':
    import sys

    for query in (
                  'title::phrase(the zope book) and author::and(michel pelletier)',
                  'title::phrase(the zope book) and author::and(michel pelletier)',
                  'a b',
                  'c++ Algol68',
                  'field:value',
                  'NEAR(a b c)',
                  'NEAR(a b c*)',
                  'phrase(the quick brown fox)',
                  'phrase(foo bar sucks)',
                  'phrase(foo bar sucks) or  OR(foo bar)',
                  '"a and b" ',
                  '(a b)',
                  'somefield::AND(a b)',
                  ):
        print '-'*80
        print '>>',query

        print EnglishQueryParser.lexer(query)
        print EnglishQueryParser.parse(query)

    if len(sys.argv) > 1:
        print '-'*80
        print '>>',sys.argv[1]
        print EnglishQueryParser.lexer(sys.argv[1])
        print EnglishQueryParser.parse(sys.argv[1])

