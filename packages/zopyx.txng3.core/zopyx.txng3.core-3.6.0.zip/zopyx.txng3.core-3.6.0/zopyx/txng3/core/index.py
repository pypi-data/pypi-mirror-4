##########################################################################
# TextIndexNG V 3
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

"""
The indexer class

$Id: index.py 2260 2010-06-23 06:11:24Z zagy $
"""
import sys

from zope.component import createObject
from zope.component import getUtility
from zope.interface import implements
from BTrees.OOBTree import OOBTree

from evaluator import Evaluator
from compatible import Persistent
from content import extract_content
from config import defaults
from resultset import unionResultSets
from util import handle_exc
from searchrequest import SearchRequest
from stemmer import getStemmer
from zopyx.txng3.core.exceptions import StorageException
from zopyx.txng3.core.interfaces import (
    IIndex, IParser, IStopwords, INormalizer, IStorageWithTermFrequency,
    IRanking)
from zopyx.txng3.core.parsetree import node_splitter, stopword_remover


class Index(Persistent, object):

    implements(IIndex)

    ranking_method = defaults['ranking_method']

    def __init__(self, **kw):

        # perform argument check first
        illegal_args = [k for k in kw.keys() if not k in defaults.keys()]
        if illegal_args:
            raise ValueError('Unknown parameters: %s' % ', '.join(illegal_args))

        # setup preferences using default args (preferences are stored as
        # attributes of the index instance

        for k,v in defaults.items():
            v = kw.get(k, v)
            setattr(self, k, v)

        self.clear()


    def clear(self):

        # lexicon & storage
        self._lexicon = createObject(self.lexicon, self.languages)

        # build either a mapping of storages when using dedicated storages
        # otherwise use a single storage

        self._feature_ranking = False    # this index supports ranking?

        if self.dedicated_storage:
            self._storage = OOBTree()
            for f in self.fields:
                self._storage[f] = createObject(self.storage)
                self._feature_ranking = IStorageWithTermFrequency.providedBy(self._storage[f])
        else:
            self._storage = createObject(self.storage)
            self._feature_ranking = IStorageWithTermFrequency.providedBy(self._storage)


    def getLexicon(self):
        """ return the lexicon """
        return self._lexicon


    def getStorage(self, field):
        """ return the storage """

        if self.dedicated_storage:
            try:
                return self._storage[field]
            except KeyError:
                raise ValueError("No such storage for field '%s'" % field)
        else:
            return self._storage


    def getSettings(self):
        """ returns a mapping contains the indexes preferences """
        from copy import copy
        d = {}
        for k in defaults.keys():
            d[k] = copy(getattr(self, k))
        return d


    def index_object(self, obj, docid):
        """ index a given object under a given document id """

        # Call the content extractor which is responsible for
        # the extraction of all related content parts from obj
        # based on the object type and the index settings.
        # The extractor should return a dictionary that maps
        # all fields of the index to a dictionary the following
        # key-value pairs:
        # 'language' -> language
        # 'content' -> content of particular field in obj as unicode
        #              string

        try:
            indexable_content = extract_content(self.fields,
                                                obj,
                                                default_encoding=self.default_encoding,
                                                default_language=self.languages[0])
        except:
            handle_exc('extract_content failed', obj, sys.exc_info())
            return False

        if indexable_content is None or not indexable_content:
            return False

        # now iterate over all fields and pass all field related content
        # through the indexer pipeline

        all_wordids = []   # we need this only if dedicated_storage == False

        for field in [f for f in self.fields if f in indexable_content.getFields()]:
            wordids = []

            for info in indexable_content.getFieldData(field):
                content = info['content']

                if not isinstance(content, unicode):
                    raise ValueError('Content must be unicode: %s' % repr(content))

                # If a document has an unknown language (other than the ones configured
                # for the index), an exception will be raised or the content is
                # indexed under the first configured language

                language = info['language']

                if not language in self.languages:
                    if self.index_unknown_languages:
                        language = self.languages[0]
                    else:
                        raise ValueError('Unsupported language: %s (allowed: %s)' % (language, ', '.join(self.languages)))

                # run content through the pipline (splitter, stopword remover, normalizer etc)
                words = self._process_words(content, language)

                # now obtain wordids from the lexicon for all words
                wordids.extend(self._lexicon.insertWords(words, language))

            # If we have dedicated storages for every field then we must insert the
            # wordids here otherwise we collect all wordids and insert them into
            # the default storage. This implies that one should use dedicated storages
            # when indexing multiple fields. If you index multiple fields without
            # dedicated storage you will not be able to search by-field.

            if self.dedicated_storage:
                try:
                    old_ids = self._storage[field].getWordIdsForDocId(docid)
                except StorageException:
                    old_ids = []

                if old_ids != wordids:
                    self._storage[field].insertDocument(docid, wordids)
            else:
                all_wordids.extend(wordids)

        # Insert everything into the default storage when not using dedicated
        # storages
        if not self.dedicated_storage:
            try:
                old_ids = self._storage.getWordIdsForDocId(docid)
            except StorageException:
                old_ids = []

            if old_ids != all_wordids:
                self._storage.insertDocument(docid, all_wordids)

        return True


    def _process_words(self, content, language):
        """ implements the processing pipeline """

        # first normalize content string
        if self.use_normalizer:
            normalizer = getUtility(INormalizer)
            content = normalizer.process(content, language)

        # now create a new splitter
        splitter = createObject(self.splitter,
                                casefolding=self.splitter_casefolding,
                                separator=self.splitter_additional_chars,
                                maxlen=self.splitter_max_length,
                               )

        # and split unicode content into list of unicode strings
        words = splitter.split(content)

        # now filter out all stopwords
        if self.use_stopwords:
            sw_utility = getUtility(IStopwords)
            words = sw_utility.process(words, language)

        # Stem words if required. If no stemmer for 'language' is available
        # then do not stem
        if self.use_stemmer:
            S = getStemmer(language)
            if S:
                words = S.stem(words)

        return words


    def unindex_object(self, docid):
        """ remove a document given its document id from the index """

        if self.dedicated_storage:
            for field in self.fields:
                self._storage[field].removeDocument(docid)
        else:
            self._storage.removeDocument(docid)


    def _prepare_query(self, query, language):
        """ performs similar transformations as _process_words() but
            only for a query. So we don't need the splitter etc.
        """

        # to lowercase if necessary
        if self.splitter_casefolding:
            query = query.lower()

        # normalize query string
        if self.use_normalizer:
            normalizer = getUtility(INormalizer)
            query = normalizer.process(query, language)

        return query


    query_options = ('parser', 'language',
                     'field', 'search_all_fields',
                     'autoexpand',
                     'similarity_ratio', 'thesaurus',
                     'ranking', 'ranking_maxhits')

    def search(self, query, **kw):
        """ Perform a query against the index. Valid query options are:

            'parser' -- named utility implementing IParser
            'language' -- language to be used to lookup words from the lexicon
            'field' -- perform searches against a configured index field
            'autoexpand' -- off|always|on_miss (see below)
        """

        # queries must be unicode
        if not isinstance(query, unicode):
            raise ValueError('Query must be unicode string')

        # First check query options
        for k in kw.keys():
            if not k in self.query_options:
                raise ValueError('Unknown option: %s (supported query options: %s)' % (k, ', '.join(self.query_options)))

        # obtain parser ID (which is the name of named utility implementing IParser)
        parser_id = kw.get('parser', self.query_parser)

        # determine query language
        language = kw.get('language', self.languages[0])
        if not language in self.languages:
            raise ValueError('Unsupported language: %s (supported languages: %s)' % (language, ', '.join(self.languages)))

        # check if field is known to the index
        field = kw.get('field')
        search_all_fields = kw.get('search_all_fields')
        if field and search_all_fields:
            raise ValueError('Cannot specify field and search_all_fields')
        if search_all_fields:
            if not self.dedicated_storage:
                raise ValueError(
                    'search_all_fields cannot be used without dedicated '
                    'storage.')
            search_fields = self.fields
        else:
            if not field:
                field = self.fields[0]
            if field not in self.fields:
                raise ValueError('Unknown field: %s (known fields: %s)' % (
                    field, ', '.join(self.fields)))
            search_fields = [field]

        # perform optional cosine ranking after searching
        ranking = bool(kw.get('ranking', self.ranking))
        if ranking and not self._feature_ranking:
            raise ValueError("The storage used for this index does not support relevance ranking")

        # Limit *ranked* result set to at most XXX hits
        ranking_maxhits = kw.get('ranking_maxhits', 50)
        if not isinstance(ranking_maxhits, int):
            raise ValueError('"ranking_maxhits" must be an integer')
        if kw.has_key('ranking_maxhits') and not ranking:
            raise ValueError('Specify "ranking_maxhits" only with having set ranking=True')

        # autoexpansion of query terms
        # 'off' -- expand never
        # 'always' -- expand always
        # 'on_miss' -- expand only for not-found terms in the query string
        autoexpand = kw.get('autoexpand', self.autoexpand)
        if not autoexpand in ('off', 'always', 'on_miss'):
            raise ValueError('"autoexpand" must either be "off", "always" or "on_miss"')

        # Use a sequence of configured thesauri (identified by their configured name)
        # for additional lookup of terms
        thesaurus = kw.get('thesaurus', [])
        if isinstance(thesaurus, str):
            thesaurus = (thesaurus,)
        if not isinstance(thesaurus, (list, tuple)):
            raise ValueError('"thesaurus" must be list or tuple of configured thesaurus ids')

        # Similarity ratio (measured as Levenshtein distance)
        similarity_ratio = float(kw.get('similarity_ratio', 0.75))
        if similarity_ratio < 0.0 or similarity_ratio > 1.0:
            raise ValueError('similarity_ratio must been 0.0 and 1.0 (value %f)' % similarity_ratio)

        # obtain a parser (registered  as named utility)
        parser = getUtility(IParser, parser_id)

        # run query string through normalizer, case normalizer etc.
        query = self._prepare_query(query, language)

        # create a tree of nodes
        parsed_query = parser.parse(query)

        if not parsed_query:
            raise ValueError('No query specified')

        # Post-filter for stopwords. We need to perform this
        # outside the query parser because the lex/yacc-based query
        # parser implementation can't be used in a reasonable way
        # to deal with such additional functionality.

        if self.use_stopwords:
            sw_utility = getUtility(IStopwords)
            stopwords = sw_utility.stopwordsForLanguage(language)

            if stopwords:
                # The stopword remover removes WordNodes representing
                # a stopword *in-place*
                stopword_remover(parsed_query, stopwords)

        # Split word nodes with the splitter
        splitter = createObject(self.splitter,
                                casefolding=self.splitter_casefolding,
                                separator=self.splitter_additional_chars,
                                maxlen=self.splitter_max_length,
                               )
        parsed_query = node_splitter(parsed_query, splitter)


        # build an instance for the search
        resultsets = []
        for field in search_fields:
            sr = SearchRequest(self,
                               query=query,
                               parsetree=parsed_query,
                               field=field,
                               autoexpand=autoexpand,
                               similarity_ratio=similarity_ratio,
                               thesaurus=thesaurus,
                               language=language)

            # call the evaluator and produce a ResultSet instance
            resultsets.append(Evaluator(sr).run())
        resultset = unionResultSets(resultsets)

        # optional ranking using the cosine measure or another configure
        # ranking method
        if ranking:
            ranking_method = getUtility(IRanking, name=self.ranking_method)
            resultset.ranking(ranking_method,
                              index=self,
                              language=language,
                              nbest=ranking_maxhits)

        return resultset


    ############################################################
    # index attributes defined as properties
    ############################################################

    def _setUse_stemmer(self, value):
        if not value in (True, False, 0, 1):
            raise ValueError('"use_stemmer" must be either True or False')
        self._use_stemmer= bool(value)

    def _getUse_stemmer(self):
        return self._use_stemmer

    use_stemmer = property(_getUse_stemmer, _setUse_stemmer)


    def _setSplitter(self, value):
        self._splitter = value

    def _getSplitter(self):
        return self._splitter

    splitter = property(_getSplitter, _setSplitter)


    def _setLexicon(self, value):
        self.__lexicon = value  # using __lexicon instead of __lexicon to avoid a name clash                                   # (_lexicon is the lexicon object)

    def _getLexicon(self):
        return self.__lexicon

    lexicon = property(_getLexicon, _setLexicon)

    def _setDedicated_storage(self, value):
        if not value in (True, False):
            raise ValueError('"dedicated_storage" must be True or False')
        self._dedicated_storage = value

    def _getDedicated_storage(self):
        return self._dedicated_storage

    dedicated_storage = property(_getDedicated_storage, _setDedicated_storage)


    def _setSplitter_max_length(self, value):
        self._splitter_max_length = value

    def _getSplitter_max_length(self):
        return self._splitter_max_length

    splitter_max_length = property(_getSplitter_max_length, _setSplitter_max_length)


    def _setFields(self, value):
        self._fields = value

    def _getFields(self):
        return self._fields

    fields = property(_getFields, _setFields)


    def _setUse_normalizer(self, value):

        if not value in (True, False):
            raise ValueError('"use_normalizer" must be True or False')
        self._use_normalizer = value

    def _getUse_normalizer(self):
        return self._use_normalizer

    use_normalizer = property(_getUse_normalizer, _setUse_normalizer)


    def _setstorage(self, value):
        self.__storage = value

    def _getstorage(self):
        return self.__storage

    storage = property(_getstorage, _setstorage)

    def _setDefault_encoding(self, value):
        self._default_encoding = value

    def _getDefault_encoding(self):
        return self._default_encoding

    default_encoding = property(_getDefault_encoding, _setDefault_encoding)


    def _setLanguages(self, value):

        if not isinstance(value, (list, tuple)):
            raise ValueError('"languages" must be list or tuple of country codes')
        if not value:
            raise ValueError('No languages given')

        self._languages = value

    def _getLanguages(self):
        return self._languages

    languages = property(_getLanguages, _setLanguages)


    def _setSplitter_additional_chars(self, value):
        self._splitter_additional_chars = value

    def _getSplitter_additional_chars(self):
        value = getattr(self, '_splitter_additional_chars', None)
        if value is None:
            return self._splitter_separators
        return value

    splitter_additional_chars = property(_getSplitter_additional_chars, _setSplitter_additional_chars)


    def _setQuery_parser(self, value):
        self._query_parser = value

    def _getQuery_parser(self):
        return self._query_parser

    query_parser = property(_getQuery_parser, _setQuery_parser)


    def _setSplitter_casefolding(self, value):

        if not value in (True, False):
            raise ValueError('"splitter_casefolding" must be True or False')

        self._splitter_casefolding = value

    def _getSplitter_casefolding(self):
        return self._splitter_casefolding

    splitter_casefolding = property(_getSplitter_casefolding, _setSplitter_casefolding)


    def _setIndex_unknown_languages(self, value):
        self._index_unknown_languages = value

    def _getIndex_unknown_languages(self):
        return self._index_unknown_languages

    index_unknown_languages = property(_getIndex_unknown_languages, _setIndex_unknown_languages)


    def _setAutoexpand(self, value):
        self._autoexpand = value

    def _getAutoexpand(self):
        return getattr(self, '_autoexpand', 'off')

    autoexpand = property(_getAutoexpand, _setAutoexpand)


    def _setAutoexpand_limit(self, value):
        self._autoexpand_limit = value

    def _getAutoexpand_limit(self):
        return self._autoexpand_limit

    autoexpand_limit = property(_getAutoexpand_limit, _setAutoexpand_limit)


    def _setRanking(self, value):
        self._ranking = value

    def _getRanking(self):
        return self._ranking

    ranking = property(_getRanking, _setRanking)


    def _setUse_stopwords(self, value):

        if not value in (True, False):
            raise ValueError('"use_stopwords" must be True or False')

        self._use_stopwords = value

    def _getUse_stopwords(self):
        return self._use_stopwords

    use_stopwords = property(_getUse_stopwords, _setUse_stopwords)


    ############################################################
    # Some helper methods
    ############################################################

    def _dump(self):
        """ perform low-level dump of the index """

        print 'Lexicon'
        for lang in self.getLexicon().getLanguages():
            print lang
            for k,v in self.getLexicon()._words[lang].items():
                print repr(k), v

            print

        print '-'*80

        print 'Storage'
        for field in self.fields:
            S = self.getStorage(field)

            for k, v in S._wid2doc.items():
                print k, list(v)


    def __repr__(self):
        return '%s[%s]' % (self.__class__.__name__, ', '.join(['%s=%s' % (k, repr(getattr(self, k, None))) for k in defaults.keys()]))

    def __len__(self):
        if self.dedicated_storage:
            return sum([len(s) for s in self._storage.values()])
        else:
            return len(self._storage)
