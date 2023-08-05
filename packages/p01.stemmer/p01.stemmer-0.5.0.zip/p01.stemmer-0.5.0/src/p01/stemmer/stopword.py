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
"""Stopwords

"""

import os.path


# stopwords
STOPWORDS = {}
STOPWORD_LOCALES = {
    'da': 'danish',
    'de': 'german',
    'en': 'english',
    'es': 'spanish',
    'fi': 'finnish',
    'fr': 'french',
    'hu': 'hungarian',
    'it': 'italian',
    'nl': 'dutch',
    'no': 'norwegian',
    'pt': 'portuguese',
    'ru': 'russian',
    'sv': 'swedish',
    'tr': 'turkish', # no stemmer implemented yet
}

def setUpStopWords():
    dataDir =  os.path.join(os.path.dirname(__file__), 'data')
    for locale, language in STOPWORD_LOCALES.items():
        fName = os.path.join(dataDir, 'stopwords', language)
        STOPWORDS[locale] = [unicode(e.replace('\n', ''), encoding='utf-8')
                             for e in open(fName, 'rb').readlines()]

setUpStopWords()
