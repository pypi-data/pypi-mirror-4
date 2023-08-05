###########################################################################
# TextIndexNG V 3
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

import os

DEFAULT_LANGUAGE = 'en'
DEFAULT_SPLITTER = 'txng.splitters.simple'
DEFAULT_PARSER = 'txng.parsers.en'
DEFAULT_THESAURUS = 'txng.thesaurus.default'
DEFAULT_STORAGE = 'txng.storages.default'
DEFAULT_LEXICON = 'txng.lexicons.default'
DEFAULT_ENCODING = 'iso-8859-15'
DEFAULT_ADDITIONAL_CHARS = '_-'
DEFAULT_RANKING = 'txng.ranking.cosine'
LOGGER_FILE = os.environ.get('TXNG3_LOGFILE', 'textindexng3.log')

defaults = {
    # use a per-field storage for the word -> doc mapping (allowing per-field searches)
    'dedicated_storage' : True,

    # fields to be indexed by the indexer
    'fields' : [],

    # supported languages
    'languages' : (DEFAULT_LANGUAGE,),

    # splitter to be used
    'splitter' : DEFAULT_SPLITTER,

    # make searches case-insensitive
    'splitter_casefolding' : True,

    # characters recognized as alphanum characters
    'splitter_additional_chars' : DEFAULT_ADDITIONAL_CHARS,

    # no idea what this was for :-)
    'splitter_max_length' : 30,

    # filter out language dependent stopword
    'use_stopwords' : False,

    # convert words with language dependent transformers (accents to non-accents)
    'use_normalizer' : False,

    # default autoexpansion mode
    'autoexpand' : 'off',

    # minimum size of query words to allow autoexpansion
    'autoexpand_limit' : 4,

    # default query parser to be used
    'query_parser' : DEFAULT_PARSER,

    # storage to be used
    'storage' : DEFAULT_STORAGE,

    # lexicon to be used
    'lexicon' : DEFAULT_LEXICON,

    # index documents with an unknown language under the first
    # configured language of the index
    'index_unknown_languages' : True,

    # default encoding (only used for encoding non-unicode queries
    'default_encoding' : DEFAULT_ENCODING,

    # stemming enabled?
    'use_stemmer' : False,

    # don't support ranking by default
    'ranking' : False,

    # Ranking method to use
    'ranking_method': DEFAULT_RANKING,

}
