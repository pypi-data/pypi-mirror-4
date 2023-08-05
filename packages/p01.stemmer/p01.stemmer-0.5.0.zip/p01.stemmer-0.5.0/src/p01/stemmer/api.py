###############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""Tokenizer and Stemmer API

"""

import re

from guess_language import guess_language

import p01.stemmer.stemmer
import p01.stemmer.stopword


# reference stopwords
STOPWORDS = p01.stemmer.stopword.STOPWORDS


def getStopWords(locale):
    """Returns the stop word list or None"""
    return STOPWORDS.get(locale, [])


# cleanup helper
def removeLineBreaks(txt):
    txt = txt.replace("\r"," ")
    txt = txt.replace("\n"," ")
    return txt.replace("  "," ")


TAGS = re.compile('(<(.*?)>)')

def removeTags(txt):
    return TAGS.sub('', txt)


NUMBERS_AND_PERCENT = re.compile(
    '(([0-9.]{1,2}/[0-9.]{1,2})|([0-9%]+)|([0-9.]*[0-9]+))')

def removeNumbers(txt):
    """Remove numbers including percent and */*"""
    res = NUMBERS_AND_PERCENT.sub('', txt)
    return res.replace('  ', ' ').strip()


# tokenize support
WORD_RE = re.compile('\\w+', re.U)

def doTokenize(txt, stopwords=[], minWordSize=1):
    """Split text into word tokens using word regexpression"""
    res = []
    append = res.append
    if txt:
        # first strip and lower
        txt = txt.strip()
        txt = txt.lower()
        txt = removeLineBreaks(txt)
        txt = removeTags(txt)
        for match in WORD_RE.finditer(txt):
            word = match.group()
            if word and word in stopwords:
                continue
            if word and len(word) >= minWordSize:
                append(word)
    return res


def doNGram(txt, minNGram=2, maxNGram=10, stopwords=[]):
    words = doTokenize(txt, stopwords)
    ngrams = []
    append = ngrams.append
    for word in words:
        nTokens = len(word)
        for i in xrange(nTokens):
            [append(word[i:j])
             for j in xrange(i + minNGram, min(nTokens, i + maxNGram) +1)
             if word[i:j] not in ngrams]
    return ngrams


def doEdgeNGram(txt, minNGram=2, maxNGram=10, stopwords=[]):
    words = doTokenize(txt, stopwords)
    ngrams = []
    append = ngrams.append
    for word in words:
        nTokens = len(word)
        [append(word[:i])
         for i in xrange(minNGram, min(nTokens, maxNGram) +1)
         if word[:i] not in ngrams]
    return ngrams


# locale API
def guessLocale(txt):
    lang = guess_language.guessLanguage(txt)
    if lang == guess_language.UNKNOWN:
        lang = None
    return lang


# stemmers
STEMMERS_CLASSES = {
    'da': p01.stemmer.stemmer.DanishStemmer,
    'de': p01.stemmer.stemmer.GermanStemmer,
    'en': p01.stemmer.stemmer.LancasterStemmer, # non snowball stemmer
    'es': p01.stemmer.stemmer.SpanishStemmer,
    'fi': p01.stemmer.stemmer.FinnishStemmer,
    'fr': p01.stemmer.stemmer.FrenchStemmer,
    'hu': p01.stemmer.stemmer.HungarianStemmer,
    'it': p01.stemmer.stemmer.ItalianStemmer,
    'nl': p01.stemmer.stemmer.DutchStemmer,
    'no': p01.stemmer.stemmer.NorwegianStemmer,
    'pt': p01.stemmer.stemmer.PortugueseStemmer,
    'ro': p01.stemmer.stemmer.RomanianStemmer, # no stopwords available yet
    'ru': p01.stemmer.stemmer.RussianStemmer,
    'sv': p01.stemmer.stemmer.SwedishStemmer,
}


def getStemmer(locale, stopwords=None):
    stemmerClass = STEMMERS_CLASSES.get(locale)
    if stemmerClass is not None:
        return stemmerClass(stopwords)


def stemTokens(wordTokens, locale, stopwords=None):
    """Stem a list of word tokens.
    
    Note: remove stopwords from the word token list if you like to use stopwords
    """
    stemmer = getStemmer(locale, stopwords)
    res = []
    append = res.append
    if stemmer is not None:
        for word in wordTokens:
            w = stemmer.stem(word)
            if w is not None:
                append(w)
    else:
        res = wordTokens
    return res


def removeStopWords(words, stopwords):
    if isinstance(words, basestring):
        # text
        return doTokenize(words, stopwords)
    else:
        # list, tuple or iterator of words
        return [word for word in words if not word in stopwords]
