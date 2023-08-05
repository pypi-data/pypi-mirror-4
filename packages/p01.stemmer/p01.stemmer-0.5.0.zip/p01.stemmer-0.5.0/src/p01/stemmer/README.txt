======
README
======

This package provides different tokenizer and stemmer components for convert
data usfull for search engines.

  >>> from pprint import pprint
  >>> import p01.stemmer.api
  >>> import p01.stemmer.stemmer


removeTags
----------

The removeTags method removes all tags from a given text. This is usefull if
we need plain text.

  >>> from p01.stemmer.api import removeTags

  >>> removeTags(u'<div>This is a short text</div>')
  u'This is a short text'

  >>> removeTags(u'<div>This is a short <br />text</div>')
  u'This is a short text'

  >>> removeTags(u'<div>This is a short\r\n text</div>')
  u'This is a short\r\n text'

This should also work with invalid markup since we just use a regex and parse
tag markup. Doesn't matter if a tag get closed or not or event not opened.

  >>> removeTags(
  ...     u'<div class="foo">This <bar>is</bar> a <b>short</span> text</div>')
  u'This is a short text'


removeNumbers
-------------

The removeNumbers method removes all numbers from a given text. This culd be
usefull if we need search text without phone or street numbers etc.

  >>> from p01.stemmer.api import removeNumbers

  >>> removeNumbers(u'This is a short text without number 42')
  u'This is a short text without number'

  >>> removeNumbers(u'12 mokeys')
  u'mokeys'

  >>> removeNumbers(u'I have seen the movie 2 times')
  u'I have seen the movie times'

  >>> removeNumbers(u'20 is 80% of 100%')
  u'is of'

  >>> removeNumbers(u'I have seen the movie 2 times\nand another 3 times.')
  u'I have seen the movie times\nand another times.'

  >>> removeNumbers(u'0.5 is 1/2 of 1')
  u'is of'

  >>> removeNumbers(u'0.5 is 1.0/2.0 of 1')
  u'is of'

  >>> removeNumbers(u'We are looking for (w/m)')
  u'We are looking for (w/m)'



removeLineBreaks
----------------

The removeLineBreaks method replaces line breaks with an empty space:

  >>> from p01.stemmer.api import removeLineBreaks

  >>> removeLineBreaks(u'This is a short\r\n text')
  u'This is a short text'

But removeLineBreaks doesn't remove tags.

  >>> removeLineBreaks(u'<div>This is a short\r\n text</div>')
  u'<div>This is a short text</div>'


doTokenize
----------

First let's test our tokenizer:

  >>> from p01.stemmer.api import doTokenize
  >>> doTokenize(u'Hier kommen Alex und Franz nach Hause')
  [u'hier', u'kommen', u'alex', u'und', u'franz', u'nach', u'hause']


doNGram
-------

the doNGram method can generate n-gram tokens based on a given text:

  >>> from p01.stemmer.api import doNGram
  >>> doNGram(u'Hello')
  [u'he', u'hel', u'hell', u'hello', u'el', u'ell', u'ello', u'll', u'llo', u'lo']

As you can see, an nGram result with a minNGram=2 and maxNGram=10 can explode.
Take care if you use nGram and store them as keywords in an index:

  >>> res = doNGram(u'Peter Smith, 8000 Zuerich Stadt Mitte')
  >>> len(res)
  61

  >>> res
  [u'pe', u'pet', u'pete', u'peter', u'et', u'ete', u'eter', u'te', u'ter', u'er', u'sm', u'smi', u'smit', u'smith', u'mi', u'mit', u'mith', u'it', u'ith', u'th', u'80', u'800', u'8000', u'00', u'000', u'zu', u'zue', u'zuer', u'zueri', u'zueric', u'zuerich', u'ue', u'uer', u'ueri', u'ueric', u'uerich', u'eri', u'eric', u'erich', u'ri', u'ric', u'rich', u'ic', u'ich', u'ch', u'st', u'sta', u'stad', u'stadt', u'ta', u'tad', u'tadt', u'ad', u'adt', u'dt', u'mitt', u'mitte', u'itt', u'itte', u'tt', u'tte']

As you can see, weon't get dupplicated items in the list:

  >>> from p01.stemmer.api import doNGram
  >>> doNGram(u'hello.hello')
  [u'he', u'hel', u'hell', u'hello', u'el', u'ell', u'ello', u'll', u'llo', u'lo']


doEdgeNGram
------------

the doEdgeNGram method can generate n-gram tokens based on a given text:

  >>> from p01.stemmer.api import doEdgeNGram
  >>> doEdgeNGram(u'Hello')
  [u'he', u'hel', u'hell', u'hello']

As you can see the edge n-gram is much smaller but contains only the beginning
of each word:

  >>> res = doEdgeNGram(u'Peter Smith, 8000 Zuerich Stadt Mitte')
  >>> len(res)
  25

  >>> res
  [u'pe', u'pet', u'pete', u'peter', u'sm', u'smi', u'smit', u'smith', u'80', u'800', u'8000', u'zu', u'zue', u'zuer', u'zueri', u'zueric', u'zuerich', u'st', u'sta', u'stad', u'stadt', u'mi', u'mit', u'mitt', u'mitte']


guessLocale
-----------

The package also uses the guess-langage package and offers some helper methods
for guess the language locale:

  >>> from guess_language import guess_language

  >>> from p01.stemmer.api import guessLocale

Let's test our guessLocale method:

  >>> guessLocale(u'Hier kommen Alex und Franz nach Hause')
  'de'

  >>> guessLocale(u'Here comes Alex and Franz')
  'en'

  >>> guessLocale(u'This is a short text')
  'en'

  >>> guessLocale(u'Das ist ein kurzer Text')
  'de'

  >>> guessLocale(u'Verifions que le détecteur de langues marche')
  'fr'

If you see the limitation, then you will recognize that we can't use this
method for guess a language if we search for something. A normal search phrase
is to short for guess a language:

  >>> guessLocale(u'Beispiel') is None
  True

  >>> guessLocale(u'Verifions') is None
  True


If the text is to short the method returns None and not 'UNKNOWN' like the
original method:

  >>> guessLocale('short') is None
  True


getStopWords
------------

We also support predefined stopwords lists. By default the method returns an
empty list if we ask for stopwords for an unsuported language:

  >>> p01.stemmer.api.getStopWords('42')
  []

We provide stopwords for the following language locales:

  >>> for key, stopwords in p01.stemmer.api.STOPWORDS.items():
  ...     print '%s %s' % (key, len(stopwords))
  ru 151
  fr 155
  en 128
  nl 101
  pt 203
  no 176
  sv 114
  de 231
  tr 53
  it 279
  hu 199
  fi 235
  da 94
  es 313

  >>> deStopWords = p01.stemmer.api.getStopWords('de')
  >>> p01.stemmer.api.STOPWORDS['de'] == deStopWords
  True

  >>> len(deStopWords)
  231


stemTokens
----------

There is a generic stemmer method which uses some predefined stemmers:

  >>> from p01.stemmer.api import stemTokens

  >>> deStopWords = p01.stemmer.api.STOPWORDS['de']
  >>> len(deStopWords)
  231

  >>> tokens = doTokenize(u'Hier kommen Alex und Franz nach Hause')
  
  >>> stemTokens(tokens, 'de', deStopWords)
  [u'hier', u'komm', u'alex', u'und', u'franz', u'nach', u'haus']

As you can see the stop word ``und`` is contained in the stopword list but
the stemmed tokens also catinas this word. This means the stopwrod list is
only used as a marker for not to stem this word and not for skip the word at
all.


removeStopWords
---------------

  >>> from p01.stemmer.api import removeStopWords

  >>> tokens = [u'hier', u'komm', u'alex', u'und', u'franz', u'nach', u'haus']
  >>> deStopWords = p01.stemmer.api.STOPWORDS['de']
  >>> removeStopWords(tokens, deStopWords)
  [u'komm', u'alex', u'franz', u'haus']


LancasterStemmer (english)
--------------------------

For stemming english words, you can choose between the PorterStemmer or the
LancasterStemmer. The Porter stemming algorithm is the oldest stemming
algorithm, originally published in 1979:

  >>> stemmer = p01.stemmer.stemmer.LancasterStemmer()
  >>> word = u'maximum'
  >>> stemmer.stem(word)
  u'maxim'

  >>> for word in (
  ...    u'maximum',    # Remove "-um" when word is intact
  ...    u'presumably', # Don't remove "-um" when word is not intact
  ...    u'multiply',   # No action taken if word ends with "-ply" 
  ...    u'provision',  # Replace "-sion" with "-j" to trigger "j" set of rules
  ...    u'owed',       # Word starting with vowel must contain at least 2 letters
  ...    u'ear',        # ditto.
  ...    u'saying',     # Words starting with consonant must contain at least 3 
  ...    u'crying',     #     letters and one of those letters must be a vowel
  ...    u'string',     # ditto.
  ...    u'meant',      # ditto.
  ...    u'cement',     # ditto.
  ...    u'cementit'):  # not convertet to cem like cement
  ...    stemmed_word = stemmer.stem(word)
  ...    print "%-20s%-20s" % (word, stemmed_word)
  maximum             maxim
  presumably          presum
  multiply            multiply
  provision           provid
  owed                ow
  ear                 ear
  saying              say
  crying              cry
  string              string
  meant               meant
  cement              cem
  cementit            cementit


PorterStemmer (english)
-----------------------

The lancaster stemming is much newer as the proter algorithm, published in
1990, and can be more aggressive than the Porter stemming algorithm.

  >>> stemmer = p01.stemmer.stemmer.PorterStemmer()
  >>> word = u'maximum'
  >>> stemmer.stem(word)
  u'maximum'

  >>> for word in (
  ...    u'maximum',    # nothing
  ...    u'presumably', # remove ably
  ...    u'multiply',   # replace y with 1 
  ...    u'provision',  # remove ion
  ...    u'owed',       # Word starting with vowel must contain at least 2 letters
  ...    u'ear',        # nothing
  ...    u'saying',     # replace ying with i
  ...    u'crying',     # remove ing
  ...    u'string',     # nothing
  ...    u'meant',      # nothing
  ...    u'cement',     # nothing
  ...    u'cementit'):  # nothing
  ...    stem = stemmer.stem(word)
  ...    print "%-20s%-20s" % (word, stem)
  maximum             maximum
  presumably          presum
  multiply            multipli
  provision           provis
  owed                ow
  ear                 ear
  saying              sai
  crying              cry
  string              string
  meant               meant
  cement              cement
  cementit            cementit

As you can see the proter stemmer is less agressive like the lancaster stemmer.


RSLPStemmer (portuguese)
-----------------------

The RSLP stemmer (Removedor de Sufixos da Lingua Portuguesa) is used for the
portuguese language.

  >>> stemmer = p01.stemmer.stemmer.RSLPStemmer()
  >>> word = u'maximum'
  >>> stemmer.stem(word)
  u'maximum'

  >>> text = u"""
  ... Clarissa risca com giz no quadro-negro a paisagem que os alunos devem
  ... copiar. Uma casinha de porta e janela, em cima duma coxilha. Um 
  ... coqueiro do lado (onde o nosso amor nasceu - pensa ela no momento mesmo 
  ... em que risca o troco longo e fino). Depois, uma estradinha que corre, 
  ... ondulando como uma cobra, e se perde longe no horizonte. Nuvens de fiz 
  ... do céu preto, um sol redondoe gordo, chispando raios, árvores, 
  ... uma lagoa com marrecos nadando ...
  ... """

  >>> for word in text.split():
  ...    stem = stemmer.stem(word)
  ...    print u"%-20r%-20r" % (word, stem)
  u'Clarissa'         u'clariss'
  u'risca'            u'risc'
  u'com'              u'com'
  u'giz'              u'giz'
  u'no'               u'no'
  u'quadro-negro'     u'quadro-negr'
  u'a'                u'a'
  u'paisagem'         u'pais'
  u'que'              u'que'
  u'os'               u'os'
  u'alunos'           u'alun'
  u'devem'            u'dev'
  u'copiar.'          u'copiar.'
  u'Uma'              u'uma'
  u'casinha'          u'cas'
  u'de'               u'de'
  u'porta'            u'port'
  u'e'                u'e'
  u'janela,'          u'janela,'
  u'em'               u'em'
  u'cima'             u'cim'
  u'duma'             u'dum'
  u'coxilha.'         u'coxilha.'
  u'Um'               u'um'
  u'coqueiro'         u'coqu'
  u'do'               u'do'
  u'lado'             u'lad'
  u'(onde'            u'(ond'
  u'o'                u'o'
  u'nosso'            u'noss'
  u'amor'             u'am'
  u'nasceu'           u'nasc'
  u'-'                u'-'
  u'pensa'            u'pens'
  u'ela'              u'ela'
  u'no'               u'no'
  u'momento'          u'moment'
  u'mesmo'            u'mesm'
  u'em'               u'em'
  u'que'              u'que'
  u'risca'            u'risc'
  u'o'                u'o'
  u'troco'            u'troc'
  u'longo'            u'long'
  u'e'                u'e'
  u'fino).'           u'fino).'
  u'Depois,'          u'depois,'
  u'uma'              u'uma'
  u'estradinha'       u'estr'
  u'que'              u'que'
  u'corre,'           u'corre,'
  u'ondulando'        u'ondul'
  u'como'             u'com'
  u'uma'              u'uma'
  u'cobra,'           u'cobra,'
  u'e'                u'e'
  u'se'               u'se'
  u'perde'            u'perd'
  u'longe'            u'long'
  u'no'               u'no'
  u'horizonte.'       u'horizonte.'
  u'Nuvens'           u'nuv'
  u'de'               u'de'
  u'fiz'              u'fiz'
  u'do'               u'do'
  u'c\xe9u'           u'c\xe9u'
  u'preto,'           u'preto,'
  u'um'               u'um'
  u'sol'              u'sol'
  u'redondoe'         u'redondo'
  u'gordo,'           u'gordo,'
  u'chispando'        u'chisp'
  u'raios,'           u'raios,'
  u'\xe1rvores,'      u'\xe1rvores,'
  u'uma'              u'uma'
  u'lagoa'            u'lago'
  u'com'              u'com'
  u'marrecos'         u'marrec'
  u'nadando'          u'nad'
  u'...'              u'...'


DanishStemmer (danish)
----------------------

The following stemmer are based on the snowball stemming pattern. Le't first
test the danish stemmer:

  >>> stopwords = p01.stemmer.api.getStopWords('da')
  >>> stemmer = p01.stemmer.stemmer.DanishStemmer(stopwords)
  >>> word = u'abarimbjergene'
  >>> stemmer.stem(word)
  u'abarimbjerg'

  >>> for word in (
  ...    u'abarimbjergene',
  ...    u'abarimbjerget',
  ...    u'abdeels',
  ...    u'abels',
  ...    u'abibajils',
  ...    u'abiezers',
  ...    u'abiezriten',
  ...    u'abiezriterne',
  ...    u'abiezriternes',
  ...    u'abarimbjergene',
  ...    u'abihajils'):
  ...    stemmed_word = stemmer.stem(word)
  ...    print "%-20s%-20s" % (word, stemmed_word)
  abarimbjergene      abarimbjerg
  abarimbjerget       abarimbjerg
  abdeels             abdeel
  abels               abel
  abibajils           abibajil
  abiezers            abiez
  abiezriten          abiezrit
  abiezriterne        abiezrit
  abiezriternes       abiezrit
  abarimbjergene      abarimbjerg
  abihajils           abihajil


DutchStemmer (dutch)
-------------------

  >>> stopwords = p01.stemmer.api.getStopWords('nl')
  >>> stemmer = p01.stemmer.stemmer.DutchStemmer(stopwords)
  >>> word = u'abiezriten'
  >>> stemmer.stem(word)
  u'abiezrit'

  >>> for word in (
  ...    u'abiel',
  ...    u'abiezer',
  ...    u'abiezers',
  ...    u'abiezriten',
  ...    u'abiezriterne',
  ...    u'abiezriternes',
  ...    u'abigajil',
  ...    u'abih',
  ...    u'abihajil'):
  ...    stemmed_word = stemmer.stem(word)
  ...    print "%-20s%-20s" % (word, stemmed_word)
  abiel               abiel
  abiezer             abiezer
  abiezers            abiezer
  abiezriten          abiezrit
  abiezriterne        abiezritern
  abiezriternes       abiezriternes
  abigajil            abigajil
  abih                abih
  abihajil            abihajil


FinnishStemmer (finnish)
------------------------

  >>> stopwords = p01.stemmer.api.getStopWords('fi')
  >>> stemmer = p01.stemmer.stemmer.FinnishStemmer(stopwords)
  >>> word = u'aachenin'
  >>> stemmer.stem(word)
  u'aachen'

  >>> for word in (
  ...    u'aachenin',
  ...    u'aachenista',
  ...    u'aadolf',
  ...    u'aadolfin',
  ...    u'aage',
  ...    u'aagot',
  ...    u'aah',
  ...    u'aake',
  ...    u'aakkoset'):
  ...    stemmed_word = stemmer.stem(word)
  ...    print "%-20s%-20s" % (word, stemmed_word)
  aachenin                      aachen
  aachenista                    aachen
  aadolf                        aadolf
  aadolfin                      aadolf
  aage                          aage
  aagot                         aago
  aah                           aah
  aake                          aake
  aakkoset                      aakkos


FrenchStemmer (french)
----------------------

  >>> stopwords = p01.stemmer.api.getStopWords('fr')
  >>> stemmer = p01.stemmer.stemmer.FrenchStemmer(stopwords)
  >>> word = u'difficile'
  >>> stemmer.stem(word)
  u'difficil'

  >>> for word in (
  ...    u'différents',
  ...    u'différer',
  ...    u'difficile',
  ...    u'difficilement',
  ...    u'difficiles',
  ...    u'difficulté',
  ...    u'difficultés',
  ...    u'difficultueux',
  ...    u'difforme'):
  ...    stemmed_word = stemmer.stem(word)
  ...    print "%-30r%-30r" % (word, stemmed_word)
  u'diff\xe9rents'              u'diff\xe9rent'
  u'diff\xe9rer'                u'differ'
  u'difficile'                  u'difficil'
  u'difficilement'              u'difficil'
  u'difficiles'                 u'difficil'
  u'difficult\xe9'              u'difficult'
  u'difficult\xe9s'             u'difficult'
  u'difficultueux'              u'difficultu'
  u'difforme'                   u'difform'


GermanStemmer (german)
----------------------

  >>> stopwords = p01.stemmer.api.getStopWords('de')
  >>> stemmer = p01.stemmer.stemmer.GermanStemmer(stopwords)
  >>> word = u'abbrechen'
  >>> stemmer.stem(word)
  u'abbrech'

  >>> for word in (
  ...    u'abbiss',
  ...    u'abbrechen',
  ...    u'abbruch',
  ...    u'abend',
  ...    u'abendbrot',
  ...    u'abenddämmerung',
  ...    u'abenddunklen',
  ...    u'abende'):
  ...    stemmed_word = stemmer.stem(word)
  ...    print "%-30r%-30r" % (word, stemmed_word)
  u'abbiss'                     u'abbiss'
  u'abbrechen'                  u'abbrech'
  u'abbruch'                    u'abbruch'
  u'abend'                      u'abend'
  u'abendbrot'                  u'abendbrot'
  u'abendd\xe4mmerung'          u'abenddammer'
  u'abenddunklen'               u'abenddunkl'
  u'abende'                     u'abend'


HungarianStemmer (hungarian)
----------------------------

  >>> stopwords = p01.stemmer.api.getStopWords('hu')
  >>> stemmer = p01.stemmer.stemmer.HungarianStemmer(stopwords)
  >>> word = u'abrosszal'
  >>> stemmer.stem(word)
  u'abrosz'

  >>> for word in (
  ...    u'abroncs',
  ...    u'abrosszal',
  ...    u'abrosz',
  ...    u'abszolutisztikus',
  ...    u'abszolutizmus',
  ...    u'abszolváltam',
  ...    u'abszolvál',
  ...    u'abszolúciót'):
  ...    stemmed_word = stemmer.stem(word)
  ...    print "%-30r%-30r" % (word, stemmed_word)
  u'abroncs'                    u'abroncs'
  u'abrosszal'                  u'abrosz'
  u'abrosz'                     u'abrosz'
  u'abszolutisztikus'           u'abszolutisztikus'
  u'abszolutizmus'              u'abszolutizmus'
  u'abszolv\xe1ltam'            u'abszolv\xe1lt'
  u'abszolv\xe1l'               u'abszolv\xe1l'
  u'abszol\xfaci\xf3t'          u'abszol\xfaci\xf3'


ItalianStemmer (italian)
------------------------

  >>> stopwords = p01.stemmer.api.getStopWords('it')
  >>> stemmer = p01.stemmer.stemmer.ItalianStemmer(stopwords)
  >>> word = u'abakoumova'
  >>> stemmer.stem(word)
  u'abakoumov'

  >>> for word in (
  ...    u'ab',
  ...    u'abakoumova',
  ...    u'abano',
  ...    u'abate',
  ...    u'abati',
  ...    u'abbacinare',
  ...    u'abbacinati',
  ...    u'abbadia',
  ...    u'abbado',
  ...    u'abbagliaron'):
  ...    stemmed_word = stemmer.stem(word)
  ...    print "%-20s%-20s" % (word, stemmed_word)
  ab                            ab
  abakoumova                    abakoumov
  abano                         aban
  abate                         abat
  abati                         abat
  abbacinare                    abbacin
  abbacinati                    abbacin
  abbadia                       abbad
  abbado                        abbad
  abbagliaron                   abbagliaron


NorwegianStemmer (norwegian)
----------------------------

  >>> stopwords = p01.stemmer.api.getStopWords('no')
  >>> stemmer = p01.stemmer.stemmer.NorwegianStemmer(stopwords)
  >>> word = u'absorberes'
  >>> stemmer.stem(word)
  u'absorber'

  >>> for word in (
  ...    u'absorberes',
  ...    u'ad',
  ...    u'adgang',
  ...    u'adgangen',
  ...    u'adkomst',
  ...    u'adkomstdokument',
  ...    u'adkomstdokumenter',
  ...    u'adkomsten',
  ...    u'adlyde'):
  ...    stemmed_word = stemmer.stem(word)
  ...    print "%-20s%-20s" % (word, stemmed_word)
  absorberes                    absorber
  ad                            ad
  adgang                        adgang
  adgangen                      adgang
  adkomst                       adkomst
  adkomstdokument               adkomstdokument
  adkomstdokumenter             adkomstdokument
  adkomsten                     adkomst
  adlyde                        adlyd


PortugueseStemmer (portuguese)
------------------------------

  >>> stopwords = p01.stemmer.api.getStopWords('pt')
  >>> stemmer = p01.stemmer.stemmer.PortugueseStemmer(stopwords)
  >>> word = u'abandonou'
  >>> stemmer.stem(word)
  u'abandon'

  >>> for word in (
  ...    u'abandonou',
  ...    u'abarrotado',
  ...    u'abarrotados',
  ...    u'abarrotou',
  ...    u'abastada',
  ...    u'abastado',
  ...    u'abastados',
  ...    u'abastecem',
  ...    u'abastecer'):
  ...    stemmed_word = stemmer.stem(word)
  ...    print "%-20s%-20s" % (word, stemmed_word)
  abandonou                     abandon
  abarrotado                    abarrot
  abarrotados                   abarrot
  abarrotou                     abarrot
  abastada                      abast
  abastado                      abast
  abastados                     abast
  abastecem                     abastec
  abastecer                     abastec


RomanianStemmer (romanian)
--------------------------

  >>> stemmer = p01.stemmer.stemmer.RomanianStemmer()
  >>> word = u'abate'
  >>> stemmer.stem(word)
  u'abat'

  >>> for word in (
  ...    u'abate',
  ...    u'abatere',
  ...    u'abateri',
  ...    u'abator',
  ...    u'abătut',
  ...    u'abătută',
  ...    u'abătuţi'):
  ...    stemmed_word = stemmer.stem(word)
  ...    print "%-30r%-30r" % (word, stemmed_word)
  u'abate'                      u'abat'
  u'abatere'                    u'abat'
  u'abateri'                    u'abater'
  u'abator'                     u'abat'
  u'ab\u0103tut'                u'ab\u0103t'
  u'ab\u0103tut\u0103'          u'ab\u0103t'
  u'ab\u0103tu\u0163i'          u'ab\u0103tu\u0163'


RussianStemmer (russian)
------------------------

  >>> stopwords = p01.stemmer.api.getStopWords('ru')
  >>> stemmer = p01.stemmer.stemmer.RussianStemmer(stopwords)
  >>> word = u"авенантненькая"
  >>> stemmer.stem(word)
  u'\u0430\u0432\u0435\u043d\u0430\u043d\u0442\u043d\u0435\u043d\u044c\u043a'

  >>> for word in (
  ...    u'авось',
  ...    u'авраама',
  ...    u'австрии',
  ...    u'австрийский',
  ...    u'автобиографию',
  ...    u'автографом',
  ...    u'автомобили',
  ...    u'автомобиль',
  ...    u'автор',
  ...    u'авторам',
  ...    u'авторитет',
  ...    u'авторитета'):
  ...    stemmed_word = stemmer.stem(word)
  ...    print "%-90r%-60r" % (word, stemmed_word)
  u'\u0430\u0432\u043e\u0441\u044c'                                                         u'\u0430\u0432'
  u'\u0430\u0432\u0440\u0430\u0430\u043c\u0430'                                             u'\u0430\u0432\u0440\u0430\u0430\u043c'
  u'\u0430\u0432\u0441\u0442\u0440\u0438\u0438'                                             u'\u0430\u0432\u0441\u0442\u0440'
  u'\u0430\u0432\u0441\u0442\u0440\u0438\u0439\u0441\u043a\u0438\u0439'                     u'\u0430\u0432\u0441\u0442\u0440\u0438\u0439\u0441\u043a'
  u'\u0430\u0432\u0442\u043e\u0431\u0438\u043e\u0433\u0440\u0430\u0444\u0438\u044e'         u'\u0430\u0432\u0442\u043e\u0431\u0438\u043e\u0433\u0440\u0430\u0444'
  u'\u0430\u0432\u0442\u043e\u0433\u0440\u0430\u0444\u043e\u043c'                           u'\u0430\u0432\u0442\u043e\u0433\u0440\u0430\u0444'
  u'\u0430\u0432\u0442\u043e\u043c\u043e\u0431\u0438\u043b\u0438'                           u'\u0430\u0432\u0442\u043e\u043c\u043e\u0431'
  u'\u0430\u0432\u0442\u043e\u043c\u043e\u0431\u0438\u043b\u044c'                           u'\u0430\u0432\u0442\u043e\u043c\u043e\u0431\u0438\u043b'
  u'\u0430\u0432\u0442\u043e\u0440'                                                         u'\u0430\u0432\u0442\u043e\u0440'
  u'\u0430\u0432\u0442\u043e\u0440\u0430\u043c'                                             u'\u0430\u0432\u0442\u043e\u0440'
  u'\u0430\u0432\u0442\u043e\u0440\u0438\u0442\u0435\u0442'                                 u'\u0430\u0432\u0442\u043e\u0440\u0438\u0442\u0435\u0442'
  u'\u0430\u0432\u0442\u043e\u0440\u0438\u0442\u0435\u0442\u0430'                           u'\u0430\u0432\u0442\u043e\u0440\u0438\u0442\u0435\u0442'


SpanishStemmer (spanish)
------------------------

  >>> stopwords = p01.stemmer.api.getStopWords('es')
  >>> stemmer = p01.stemmer.stemmer.SpanishStemmer(stopwords)
  >>> word = u'abastecedora'
  >>> stemmer.stem(word)
  u'abastecedor'

  >>> for word in (
  ...    u'abastecedora',
  ...    u'abastecer',
  ...    u'abastecimiento',
  ...    u'abastecimientos',
  ...    u'abasto',
  ...    u'abatares',
  ...    u'abatida',
  ...    u'abatido',
  ...    u'abatidos'):
  ...    stemmed_word = stemmer.stem(word)
  ...    print "%-20s%-20s" % (word, stemmed_word)
  abastecedora                  abastecedor
  abastecer                     abastec
  abastecimiento                abastec
  abastecimientos               abastec
  abasto                        abast
  abatares                      abatar
  abatida                       abat
  abatido                       abat
  abatidos                      abat


SwedishStemmer (swedish)
------------------------

  >>> stopwords = p01.stemmer.api.getStopWords('sv')
  >>> stemmer = p01.stemmer.stemmer.SwedishStemmer(stopwords)
  >>> word = u'ackompanjerade'
  >>> stemmer.stem(word)
  u'ackompanjer'

  >>> for word in (
  ...    u'ackompanjerade',
  ...    u'ackord',
  ...    u'acllerbring',
  ...    u'acob',
  ...    u'ad',
  ...    u'adclc',
  ...    u'adcle',
  ...    u'addra',
  ...    u'ade',
  ...    u'adeie',
  ...    u'adel',
  ...    u'adele',
  ...    u'adele'):
  ...    stemmed_word = stemmer.stem(word)
  ...    print "%-20s%-20s" % (word, stemmed_word)
  ackompanjerade      ackompanjer
  ackord              ackord
  acllerbring         acllerbring
  acob                acob
  ad                  ad
  adclc               adclc
  adcle               adcl
  addra               addr
  ade                 ade
  adeie               adei
  adel                adel
  adele               adel
  adele               adel


If you give both a stemmer and a language, the stemmer must support that
language. Both porter and lancaster can be used with any language, while
wordnet, rslp, and isri are limited to their respective languages. The snowball
stemmer currently supports 13 languages, and is the default stemmer for those
languages.
