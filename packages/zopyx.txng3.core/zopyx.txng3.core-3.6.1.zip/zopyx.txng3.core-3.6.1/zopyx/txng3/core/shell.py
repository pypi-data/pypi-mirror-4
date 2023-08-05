###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
Interactive indexer shell

$Id: shell.py 2336 2011-05-31 16:41:23Z yvoschu $
"""

import sys, os, time, atexit
import hotshot, hotshot.stats
from optparse import OptionParser

from zope.component import provideUtility
from zope.component.interfaces import IFactory
from zope.component.testing import setUp

from index import Index
from parsers.english import EnglishParser
from splitter import SplitterFactory
from stopwords import Stopwords
from zopyx.txng3.core.interfaces import IParser, IStopwords, IThesaurus
from zopyx.txng3.core.lexicon import LexiconFactory
from zopyx.txng3.core.storage import StorageWithTermFrequencyFactory
from zopyx.txng3.core.thesaurus import GermanThesaurus


# Setup environment
setUp()
provideUtility(SplitterFactory, IFactory, 'txng.splitters.default')
provideUtility(EnglishParser(), IParser, 'txng.parsers.en')
provideUtility(Stopwords(), IStopwords, 'txng.stopwords')
provideUtility(LexiconFactory, IFactory, 'txng.lexicons.default')
provideUtility(StorageWithTermFrequencyFactory, IFactory, 'txng.storages.default')
provideUtility(GermanThesaurus, IThesaurus, 'txng.thesaurus.de')


try:
    import readline
    histfile = os.path.expanduser('~/.pyhist')
    readline.read_history_file(histfile)
    atexit.register(readline.write_history_file, histfile)
except: pass


class Text:
    def __init__(self, s):
        self.SearchableText = s


parser = OptionParser()
parser.add_option('-d','--directory', action='store',type='string', default='tests/data/texts',
        dest='directory',help='directory to be search for input files')
parser.add_option('-p','--profile', action='store_true', default=False,
        dest='profile',help='perform profiling of the indexing process')
parser.add_option('-t','--thesaurus', action='store', default=None,
        dest='thesaurus',help='ID of thesaurus to be used')


options, files = parser.parse_args()

I = Index(fields=('SearchableText',), autoexpand_limit=4)

ts = time.time()
count = 0
bytes = 0  

ID2FILES = {}

def do_index(options, files):
    global count, bytes

    if not files:
        print >>sys.stderr, 'Reading files from %s' % options.directory
        files = [] 
        for dirname, dirs, filenames in os.walk(options.directory):
            for f in filenames:
                fullname = os.path.join(dirname, f)
                if f.endswith('txt'):
                    files.append(fullname)

    for docid, fname in enumerate(files):

        text = open(fname).read()
        I.index_object(Text(unicode(text, 'iso-8859-15')), docid)    
        count += 1
        bytes += len(text)
        ID2FILES[docid] = fname
        if count % 100 ==0:
            print count



if options.profile:
    prof = hotshot.Profile('indexer.prof')
    prof.runcall(do_index, options, files)

    stats = hotshot.stats.load('indexer.prof')
    stats.strip_dirs()
    stats.sort_stats('cumulative', 'calls')
    stats.print_stats(25)
else:
    do_index(options, files)

duration = time.time() - ts
print '%d documents, duration: %5.3f seconds,total size: %d bytes, speed: %5.3f bytes/second' % (count, duration, bytes, float(bytes)/duration)
    
while 1:
    query = raw_input('query> ')
    query = unicode(query, 'iso-8859-15')
    try:
        kw = {'autoexpand' : 'off',
              'ranking' : True,
              'ranking_maxhits' : 100,
              'field' : 'SearchableText',
             }
        if options.thesaurus:
            kw['thesaurus'] = options.thesaurus

        ts = time.time()

        if options.profile:
            prof = hotshot.Profile('query.prof')
            result = prof.runcall(I.search, query, **kw)
            stats = hotshot.stats.load('query.prof')
            stats.strip_dirs()
            stats.sort_stats('cumulative', 'calls')
            stats.print_stats(25)
        else:
            result = I.search(query, **kw)
        te = time.time()
        for docid,score in result.getRankedResults().items():
            print ID2FILES[docid], score
        print '%2.5lf milli-seconds' % (1000.0*(te-ts))
    except:
        import traceback
        traceback.print_exc()
