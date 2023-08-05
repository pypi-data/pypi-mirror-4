###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################

__all__ = ('getStemmer', 'availableStemmers')

from zopyx.txng3.ext import stemmer

# maps country codes to language name
country_codes = {

    'da' : 'danish', 
    'nl' : 'dutch', 
    'en' : 'english', 
    'fi' : 'finnish', 
    'fr' : 'french', 
    'de' : 'german', 
    'hu' : 'hungarian', 
    'it' : 'italian', 
    'no' : 'norwegian', 
    'pt' : 'portuguese', 
    'ro' : 'romanian',
    'ru' : 'russian', 
    'es' : 'spanish', 
    'sv' : 'swedish',
    'tr' : 'turkish',
}

availableStemmers = stemmer.availableStemmers()

def getStemmer(language):
    """ Return a Stemmer instance for a given language or country code 
        or None if no stemmer exists.
    """

    original_language = language
    if not language in availableStemmers:
        language = country_codes.get(language)
    if language:
        return stemmer.Stemmer(language)
    return None
