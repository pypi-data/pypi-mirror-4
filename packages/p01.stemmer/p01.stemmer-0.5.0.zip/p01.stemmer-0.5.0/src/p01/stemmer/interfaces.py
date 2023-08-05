###############################################################################
#
# Copyright (c) 2010 Projekt01 GmbH and Contributors.
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
"""
$Id: interfaces.py 3473 2012-11-22 13:54:35Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface


class IStemmer(zope.interface.Interface):
    """Stemmer base interface"""

    def stem(word):
        """Stem or not and return a word depending on used stopwords"""


class ILancasterStemmer(IStemmer):
    """LancasterStemmer supports the english language"""


class IPorterStemmer(IStemmer):
    """PorterStemmer supports the english language"""


class IRSLPStemmer(IStemmer):
    """Portuguese language stemmer (Removedor de Sufixos da Lingua Portuguesa)
    """


class ISnowballStemmer(IStemmer):
    """SnowballStemmer base interface"""


class IDanishStemmer(ISnowballStemmer):
    """SnowballStemmer supporting the danish language"""


class IDutchStemmer(ISnowballStemmer):
    """SnowballStemmer supporting the dutch language"""


class IFinnishStemmer(ISnowballStemmer):
    """SnowballStemmer supporting the finnish language"""


class IFrenchStemmer(ISnowballStemmer):
    """SnowballStemmer supporting the french language"""


class IGermanStemmer(ISnowballStemmer):
    """SnowballStemmer supporting the german language"""


class IHungarianStemmer(ISnowballStemmer):
    """SnowballStemmer supporting the hungarian language"""


class IItalianStemmer(ISnowballStemmer):
    """SnowballStemmer supporting the italian language"""


class INorwegianStemmer(ISnowballStemmer):
    """SnowballStemmer supporting the norwegian language"""


class IPortugueseStemmer(ISnowballStemmer):
    """SnowballStemmer supporting the portuguese language"""


class IRomanianStemmer(ISnowballStemmer):
    """SnowballStemmer supporting the romanian language"""


class IRussianStemmer(ISnowballStemmer):
    """SnowballStemmer supporting the russian language"""


class ISpanishStemmer(ISnowballStemmer):
    """SnowballStemmer supporting the spanish language"""


class ISwedishStemmer(ISnowballStemmer):
    """SnowballStemmer supporting the swedish language"""
