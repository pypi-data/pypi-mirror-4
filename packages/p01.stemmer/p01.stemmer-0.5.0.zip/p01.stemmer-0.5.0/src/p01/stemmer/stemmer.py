# -*- coding: utf-8 -*- 
###############################################################################
#
# 2011 Projekt01 GmbH and Contributors
#
# Natural Language Toolkit: RSLP Stemmer
#
# Copyright (C) 2001-2010 NLTK Project
# Author: Tiago Tresoldi <tresoldi@gmail.com>
# URL: <http://www.nltk.org/>
# For license information, see LICENSE.TXT
#
"""Stemmer implementations

"""

import os.path
import re
import sys

import zope.interface

from p01.stemmer import interfaces

# stemmers
class Stemmer(object):
    """Stemmer base class"""

    def stem(self, word):
        """Stem a word"""
        raise NotImplementedError("Subclass must implement stem method")

    def __repr__(self):
        return u'<%s with %s stopwords>' % ( self.__class__.__name__,
            len(self.stopwords))


class LancasterStemmer(Stemmer):
    """LancasterStemmer supports the english language

    This code is based on the NLTK Project which contains the following note:

    A word stemmer based on the Lancaster stemming algorithm.
    Paice, Chris D. "Another Stemmer." ACM SIGIR Forum 24.3 (1990): 56-61.

    see: http://www.comp.lancs.ac.uk/computing/research/stemming/

    """

    zope.interface.implements(interfaces.ILancasterStemmer)

    # The rule list is static since it doesn't change between instances
    rule_tuple = (
        "ai*2.",     # -ia > -   if intact 
        "a*1.",      # -a > -    if intact 
        "bb1.",      # -bb > -b   
        "city3s.",   # -ytic > -ys
        "ci2>",      # -ic > -
        "cn1t>",     # -nc > -nt  
        "dd1.",      # -dd > -d   
        "dei3y>",    # -ied > -y  
        "deec2ss.",  # -ceed >", -cess 
        "dee1.",     # -eed > -ee
        "de2>",      # -ed > -   
        "dooh4>",    # -hood > - 
        "e1>",       # -e > -
        "feil1v.",   # -lief > -liev
        "fi2>",      # -if > -   
        "gni3>",     # -ing > -  
        "gai3y.",    # -iag > -y 
        "ga2>",      # -ag > -   
        "gg1.",      # -gg > -g  
        "ht*2.",     # -th > -   if intact
        "hsiug5ct.", # -guish > -ct
        "hsi3>",     # -ish > -  
        "i*1.",      # -i > -    if intact
        "i1y>",      # -i > -y   
        "ji1d.",     # -ij > -id   --  see nois4j> & vis3j>
        "juf1s.",    # -fuj > -fus
        "ju1d.",     # -uj > -ud 
        "jo1d.",     # -oj > -od 
        "jeh1r.",    # -hej > -her
        "jrev1t.",   # -verj > -vert
        "jsim2t.",   # -misj > -mit
        "jn1d.",     # -nj > -nd 
        "j1s.",      # -j > -s   
        "lbaifi6.",  # -ifiabl > -
        "lbai4y.",   # -iabl > -y
        "lba3>",     # -abl > -  
        "lbi3.",     # -ibl > -  
        "lib2l>",    # -bil > -bl
        "lc1.",      # -cl > c   
        "lufi4y.",   # -iful > -y
        "luf3>",     # -ful > -  
        "lu2.",      # -ul > -   
        "lai3>",     # -ial > -  
        "lau3>",     # -ual > -  
        "la2>",      # -al > -   
        "ll1.",      # -ll > -l  
        "mui3.",     # -ium > -  
        "mu*2.",     # -um > -   if intact
        "msi3>",     # -ism > -  
        "mm1.",      # -mm > -m  
        "nois4j>",   # -sion > -j
        "noix4ct.",  # -xion > -ct
        "noi3>",     # -ion > -  
        "nai3>",     # -ian > -  
        "na2>",      # -an > -   
        "nee0.",     # protect  -een
        "ne2>",      # -en > -   
        "nn1.",      # -nn > -n  
        "pihs4>",    # -ship > - 
        "pp1.",      # -pp > -p  
        "re2>",      # -er > -   
        "rae0.",     # protect  -ear
        "ra2.",      # -ar > -   
        "ro2>",      # -or > -   
        "ru2>",      # -ur > -   
        "rr1.",      # -rr > -r  
        "rt1>",      # -tr > -t  
        "rei3y>",    # -ier > -y 
        "sei3y>",    # -ies > -y 
        "sis2.",     # -sis > -s 
        "si2>",      # -is > -   
        "ssen4>",    # -ness > - 
        "ss0.",      # protect  -ss
        "suo3>",     # -ous > -  
        "su*2.",     # -us > -   if intact
        "s*1>",      # -s > -    if intact
        "s0.",       # -s > -s   
        "tacilp4y.", # -plicat > -ply
        "ta2>",      # -at > -   
        "tnem4>",    # -ment > - 
        "tne3>",     # -ent > -  
        "tna3>",     # -ant > -  
        "tpir2b.",   # -ript > -rib
        "tpro2b.",   # -orpt > -orb
        "tcud1.",    # -duct > -duc
        "tpmus2.",   # -sumpt > -sum
        "tpec2iv.",  # -cept > -ceiv
        "tulo2v.",   # -olut > -olv
        "tsis0.",    # protect  -sist
        "tsi3>",     # -ist > -  
        "tt1.",      # -tt > -t  
        "uqi3.",     # -iqu > -   
        "ugo1.",     # -ogu > -og
        "vis3j>",    # -siv > -j 
        "vie0.",     # protect  -eiv
        "vi2>",      # -iv > -   
        "ylb1>",     # -bly > -bl
        "yli3y>",    # -ily > -y 
        "ylp0.",     # protect  -ply
        "yl2>",      # -ly > -   
        "ygo1.",     # -ogy > -og
        "yhp1.",     # -phy > -ph
        "ymo1.",     # -omy > -om
        "ypo1.",     # -opy > -op
        "yti3>",     # -ity > -  
        "yte3>",     # -ety > -  
        "ytl2.",     # -lty > -l 
        "yrtsi5.",   # -istry > -
        "yra3>",     # -ary > -  
        "yro3>",     # -ory > -  
        "yfi3.",     # -ify > -  
        "ycn2t>",    # -ncy > -nt
        "yca3>",     # -acy > -  
        "zi2>",      # -iz > -   
        "zy1s."      # -yz > -ys 
    )

    def __init__(self, stopwords=None):
        """Create an instance of the LancasterStemmer stemmer."""
        if stopwords is None:
            stopwords = []
        self.stopwords = set(stopwords)
        # setup an empty rule dictionary - this will be filled in later
        self.rule_dictionary = {}

    def parseRules(self, rule_tuple):
        """Validate the set of rules used in this stemmer."""
        valid_rule = re.compile("^[a-z]+\*?\d[a-z]*[>\.]?$")
        # Empty any old rules from the rule set before adding new ones
        self.rule_dictionary = {}

        for rule in rule_tuple:
            if not valid_rule.match(rule):
                raise ValueError, "The rule %s is invalid" % rule
            first_letter = rule[0:1]
            if first_letter in self.rule_dictionary:
                self.rule_dictionary[first_letter].append(rule)
            else:
                self.rule_dictionary[first_letter] = [rule]

    def stem(self, word):
        """Stem a word using the Lancaster stemmer."""
        # lower, since all the rules are lower-cased
        word = word.lower()
        # don't stem stopwords
        if word in self.stopwords:
            return word

        # Save a copy of the original word
        intact_word = word

        # If the user hasn't supplied any rules, setup the default rules
        if len(self.rule_dictionary) == 0:
            self.parseRules(LancasterStemmer.rule_tuple)

        return self.__doStemming(word, intact_word)

    def __doStemming(self, word, intact_word):
        """Perform the actual word stemming"""

        valid_rule = re.compile("^([a-z]+)(\*?)(\d)([a-z]*)([>\.]?)$")

        proceed = True

        while proceed:

            # Find the position of the last letter of the word to be stemmed
            last_letter_position = self.__getLastLetter(word)

            # Only stem the word if it has a last letter and a rule matching that last letter
            if last_letter_position < 0 or word[last_letter_position] not in self.rule_dictionary:
                proceed = False

            else:
                rule_was_applied = False

                # Go through each rule that matches the word's final letter
                for rule in self.rule_dictionary[word[last_letter_position]]:
                    rule_match = valid_rule.match(rule)
                    if rule_match:
                        (ending_string,
                         intact_flag,
                         remove_total,
                         append_string,
                         cont_flag) = rule_match.groups()

                        # Convert the number of chars to remove when stemming
                        # from a string to an integer
                        remove_total = int(remove_total)

                        # Proceed if word's ending matches rule's word ending
                        if word.endswith(ending_string[::-1]):
                            if intact_flag:
                                if (word == intact_word and
                                    self.__isAcceptable(word, remove_total)):
                                    word = self.__applyRule(word,
                                                            remove_total,
                                                            append_string)
                                    rule_was_applied = True
                                    if cont_flag == '.':
                                        proceed = False
                                    break
                            elif self.__isAcceptable(word, remove_total):
                                word = self.__applyRule(word,
                                                        remove_total,
                                                        append_string)
                                rule_was_applied = True
                                if cont_flag == '.':
                                    proceed = False
                                break
                # If no rules apply, the word doesn't need any more stemming
                if rule_was_applied == False:
                    proceed = False
        return word

    def __getLastLetter(self, word):
        """Get the zero-based index of the last alphabetic character in this
        string
        """
        last_letter = -1
        for position in range(len(word)):
            if word[position].isalpha():
                last_letter = position
            else:
                break
        return last_letter

    def __isAcceptable(self, word, remove_total):
        """Determine if the word is acceptable for stemming."""
        word_is_acceptable = False
        # If the word starts with a vowel, it must be at least 2
        # characters long to be stemmed
        if word[0] in "aeiouy":
            if (len(word) - remove_total >= 2):
                word_is_acceptable = True
        # If the word starts with a consonant, it must be at least 3
        # characters long (including one vowel) to be stemmed
        elif (len(word) - remove_total >= 3):
            if word[1] in "aeiouy":
                word_is_acceptable = True
            elif word[2] in "aeiouy":
                word_is_acceptable = True
        return word_is_acceptable

    def __applyRule(self, word, remove_total, append_string):
        """Apply the stemming rule to the word
        """
        # Remove letters from the end of the word
        new_word_length = len(word) - remove_total
        word = word[0:new_word_length]

        # And add new letters to the end of the truncated word
        if append_string:
            word += append_string
        return word


class PorterStemmer(Stemmer):
    """PorterStemmer supports the english language

    This code is based on the textmining python package which contains the
    following note:

    This is the Porter stemming algorithm, ported to Python from the
    version coded up in ANSI C by the author. It may be be regarded
    as canonical, in that it follows the algorithm presented in

    Porter, 1980, An algorithm for suffix stripping, Program, Vol. 14,
    no. 3, pp 130-137,

    only differing from it at the points maked --DEPARTURE-- below.

    See also http://www.tartarus.org/~martin/PorterStemmer

    The algorithm as described in the paper could be exactly replicated
    by adjusting the points of DEPARTURE, but this is barely necessary,
    because (a) the points of DEPARTURE are definitely improvements, and
    (b) no encoding of the Porter stemmer I have seen is anything like
    as exact as this version, even with the points of DEPARTURE!

    Vivake Gupta (v@nano.com)

    Release 1: January 2001
    """

    def __init__(self, stopwords=None):
        """The main part of the stemming algorithm starts here.
        b is a buffer holding a word to be stemmed. The letters are in b[k0],
        b[k0+1] ... ending at b[k]. In fact k0 = 0 in this demo program. k is
        readjusted downwards as the stemming progresses. Zero termination is
        not in fact used in the algorithm.

        Note that only lower case sequences are stemmed. Forcing to lower case
        should be done before stem(...) is called.
        """
        if stopwords is None:
            stopwords = []
        self.stopwords = set(stopwords)
        self.b = ""  # buffer for word to be stemmed
        self.k = 0
        self.k0 = 0
        self.j = 0   # j is a general offset into the string

    def cons(self, i):
        """cons(i) is TRUE <=> b[i] is a consonant."""
        if self.b[i] == 'a' or self.b[i] == 'e' or self.b[i] == 'i' or self.b[i] == 'o' or self.b[i] == 'u':
            return 0
        if self.b[i] == 'y':
            if i == self.k0:
                return 1
            else:
                return (not self.cons(i - 1))
        return 1

    def m(self):
        """m() measures the number of consonant sequences between k0 and j.
        if c is a consonant sequence and v a vowel sequence, and <..>
        indicates arbitrary presence,

           <c><v>       gives 0
           <c>vc<v>     gives 1
           <c>vcvc<v>   gives 2
           <c>vcvcvc<v> gives 3
           ....
        """
        n = 0
        i = self.k0
        while 1:
            if i > self.j:
                return n
            if not self.cons(i):
                break
            i = i + 1
        i = i + 1
        while 1:
            while 1:
                if i > self.j:
                    return n
                if self.cons(i):
                    break
                i = i + 1
            i = i + 1
            n = n + 1
            while 1:
                if i > self.j:
                    return n
                if not self.cons(i):
                    break
                i = i + 1
            i = i + 1

    def vowelinstem(self):
        """vowelinstem() is TRUE <=> k0,...j contains a vowel"""
        for i in range(self.k0, self.j + 1):
            if not self.cons(i):
                return 1
        return 0

    def doublec(self, j):
        """doublec(j) is TRUE <=> j,(j-1) contain a double consonant."""
        if j < (self.k0 + 1):
            return 0
        if (self.b[j] != self.b[j-1]):
            return 0
        return self.cons(j)

    def cvc(self, i):
        """cvc(i) is TRUE <=> i-2,i-1,i has the form consonant - vowel - consonant
        and also if the second c is not w,x or y. this is used when trying to
        restore an e at the end of a short  e.g.

           cav(e), lov(e), hop(e), crim(e), but
           snow, box, tray.
        """
        if i < (self.k0 + 2) or not self.cons(i) or self.cons(i-1) or not self.cons(i-2):
            return 0
        ch = self.b[i]
        if ch == 'w' or ch == 'x' or ch == 'y':
            return 0
        return 1

    def ends(self, s):
        """ends(s) is TRUE <=> k0,...k ends with the string s."""
        length = len(s)
        if s[length - 1] != self.b[self.k]: # tiny speed-up
            return 0
        if length > (self.k - self.k0 + 1):
            return 0
        if self.b[self.k-length+1:self.k+1] != s:
            return 0
        self.j = self.k - length
        return 1

    def setto(self, s):
        """setto(s) sets (j+1),...k to the characters in the string s, readjusting k."""
        length = len(s)
        self.b = self.b[:self.j+1] + s + self.b[self.j+length+1:]
        self.k = self.j + length

    def r(self, s):
        """r(s) is used further down."""
        if self.m() > 0:
            self.setto(s)

    def step1ab(self):
        """step1ab() gets rid of plurals and -ed or -ing. e.g.

           caresses  ->  caress
           ponies    ->  poni
           ties      ->  ti
           caress    ->  caress
           cats      ->  cat

           feed      ->  feed
           agreed    ->  agree
           disabled  ->  disable

           matting   ->  mat
           mating    ->  mate
           meeting   ->  meet
           milling   ->  mill
           messing   ->  mess

           meetings  ->  meet
        """
        if self.b[self.k] == 's':
            if self.ends("sses"):
                self.k = self.k - 2
            elif self.ends("ies"):
                self.setto("i")
            elif self.b[self.k - 1] != 's':
                self.k = self.k - 1
        if self.ends("eed"):
            if self.m() > 0:
                self.k = self.k - 1
        elif (self.ends("ed") or self.ends("ing")) and self.vowelinstem():
            self.k = self.j
            if self.ends("at"):   self.setto("ate")
            elif self.ends("bl"): self.setto("ble")
            elif self.ends("iz"): self.setto("ize")
            elif self.doublec(self.k):
                self.k = self.k - 1
                ch = self.b[self.k]
                if ch == 'l' or ch == 's' or ch == 'z':
                    self.k = self.k + 1
            elif (self.m() == 1 and self.cvc(self.k)):
                self.setto("e")

    def step1c(self):
        """step1c() turns terminal y to i when there is another vowel in the stem."""
        if (self.ends("y") and self.vowelinstem()):
            self.b = self.b[:self.k] + 'i' + self.b[self.k+1:]

    def step2(self):
        """step2() maps double suffices to single ones.
        so -ization ( = -ize plus -ation) maps to -ize etc. note that the
        string before the suffix must give m() > 0.
        """
        if self.b[self.k - 1] == 'a':
            if self.ends("ational"):   self.r("ate")
            elif self.ends("tional"):  self.r("tion")
        elif self.b[self.k - 1] == 'c':
            if self.ends("enci"):      self.r("ence")
            elif self.ends("anci"):    self.r("ance")
        elif self.b[self.k - 1] == 'e':
            if self.ends("izer"):      self.r("ize")
        elif self.b[self.k - 1] == 'l':
            if self.ends("bli"):       self.r("ble") # --DEPARTURE--
            # To match the published algorithm, replace this phrase with
            #   if self.ends("abli"):      self.r("able")
            elif self.ends("alli"):    self.r("al")
            elif self.ends("entli"):   self.r("ent")
            elif self.ends("eli"):     self.r("e")
            elif self.ends("ousli"):   self.r("ous")
        elif self.b[self.k - 1] == 'o':
            if self.ends("ization"):   self.r("ize")
            elif self.ends("ation"):   self.r("ate")
            elif self.ends("ator"):    self.r("ate")
        elif self.b[self.k - 1] == 's':
            if self.ends("alism"):     self.r("al")
            elif self.ends("iveness"): self.r("ive")
            elif self.ends("fulness"): self.r("ful")
            elif self.ends("ousness"): self.r("ous")
        elif self.b[self.k - 1] == 't':
            if self.ends("aliti"):     self.r("al")
            elif self.ends("iviti"):   self.r("ive")
            elif self.ends("biliti"):  self.r("ble")
        elif self.b[self.k - 1] == 'g': # --DEPARTURE--
            if self.ends("logi"):      self.r("log")
        # To match the published algorithm, delete this phrase

    def step3(self):
        """step3() dels with -ic-, -full, -ness etc. similar strategy to step2."""
        if self.b[self.k] == 'e':
            if self.ends("icate"):     self.r("ic")
            elif self.ends("ative"):   self.r("")
            elif self.ends("alize"):   self.r("al")
        elif self.b[self.k] == 'i':
            if self.ends("iciti"):     self.r("ic")
        elif self.b[self.k] == 'l':
            if self.ends("ical"):      self.r("ic")
            elif self.ends("ful"):     self.r("")
        elif self.b[self.k] == 's':
            if self.ends("ness"):      self.r("")

    def step4(self):
        """step4() takes off -ant, -ence etc., in context <c>vcvc<v>."""
        if self.b[self.k - 1] == 'a':
            if self.ends("al"): pass
            else: return
        elif self.b[self.k - 1] == 'c':
            if self.ends("ance"): pass
            elif self.ends("ence"): pass
            else: return
        elif self.b[self.k - 1] == 'e':
            if self.ends("er"): pass
            else: return
        elif self.b[self.k - 1] == 'i':
            if self.ends("ic"): pass
            else: return
        elif self.b[self.k - 1] == 'l':
            if self.ends("able"): pass
            elif self.ends("ible"): pass
            else: return
        elif self.b[self.k - 1] == 'n':
            if self.ends("ant"): pass
            elif self.ends("ement"): pass
            elif self.ends("ment"): pass
            elif self.ends("ent"): pass
            else: return
        elif self.b[self.k - 1] == 'o':
            if self.ends("ion") and (self.b[self.j] == 's' or self.b[self.j] == 't'): pass
            elif self.ends("ou"): pass
            # takes care of -ous
            else: return
        elif self.b[self.k - 1] == 's':
            if self.ends("ism"): pass
            else: return
        elif self.b[self.k - 1] == 't':
            if self.ends("ate"): pass
            elif self.ends("iti"): pass
            else: return
        elif self.b[self.k - 1] == 'u':
            if self.ends("ous"): pass
            else: return
        elif self.b[self.k - 1] == 'v':
            if self.ends("ive"): pass
            else: return
        elif self.b[self.k - 1] == 'z':
            if self.ends("ize"): pass
            else: return
        else:
            return
        if self.m() > 1:
            self.k = self.j

    def step5(self):
        """step5() removes a final -e if m() > 1, and changes -ll to -l if
        m() > 1.
        """
        self.j = self.k
        if self.b[self.k] == 'e':
            a = self.m()
            if a > 1 or (a == 1 and not self.cvc(self.k-1)):
                self.k = self.k - 1
        if self.b[self.k] == 'l' and self.doublec(self.k) and self.m() > 1:
            self.k = self.k -1

    def doStem(self, word, i, j):
        """In stem(word,i,j), word is a char pointer, and the string to be stemmed
        is from p[i] to p[j] inclusive. Typically i is zero and j is the
        offset to the last character of a string, (p[j+1] == '\0'). The
        stemmer adjusts the characters p[i] ... p[j] and returns the new
        end-point of the string, k. Stemming never increases word length, so
        i <= k <= j. To turn the stemmer into a module, declare 'stem' as
        extern, and delete the remainder of this file.
        """
        # copy the parameters into statics
        self.b = word
        self.k = j
        self.k0 = i
        if self.k <= self.k0 + 1:
            return self.b # --DEPARTURE--

        # With this line, strings of length 1 or 2 don't go through the
        # stemming process, although no mention is made of this in the
        # published algorithm. Remove the line to match the published
        # algorithm.

        self.step1ab()
        self.step1c()
        self.step2()
        self.step3()
        self.step4()
        self.step5()
        return self.b[self.k0:self.k+1]

    def stem(self, word):
        # lower, since all the rules are lower-cased
        word = word.lower()
        # don't stem stopwords
        if word in self.stopwords:
            return word

        return self.doStem(word, 0, len(word) - 1)


class RSLPStemmer(Stemmer):
    """Portuguese language stemmer (Removedor de Sufixos da Lingua Portuguesa).

    This code is based on the NLTK Project which contains the following note:

    This code is based on the algorithm presented in the paper "A Stemming
    Algorithm for the Portuguese Language" by Viviane Moreira Orengo and
    Christian Huyck, which unfortunately I had no access to. The code is a
    Python version, with some minor modifications of mine, to the description
    presented at http://www.webcitation.org/5NnvdIzOb and to the C source code
    available at http://www.inf.ufrgs.br/~arcoelho/rslp/integrando_rslp.html.
    Please note that this stemmer is intended for demostration and educational
    purposes only.

    """

    def __init__(self, stopwords=None):
        if stopwords is None:
            stopwords = []
        self.stopwords = set(stopwords)
        self._model = []
        self._model.append( self.readData("step0.pt"))
        self._model.append( self.readData("step1.pt"))
        self._model.append( self.readData("step2.pt"))
        self._model.append( self.readData("step3.pt"))
        self._model.append( self.readData("step4.pt"))
        self._model.append( self.readData("step5.pt"))
        self._model.append( self.readData("step6.pt") )

    def readData (self, filename):
        rslpDir =  os.path.join(os.path.dirname(__file__), 'data', 'rslp')
        fName = os.path.join(rslpDir, filename)
        lines = [unicode(e, encoding='utf-8')
                 for e in open(fName, 'r').readlines()]

        lines = [line for line in lines if line != u""]     # remove blank lines
        lines = [line for line in lines if line[0] != "#"]  # remove comments
  
        # NOTE: a simple but ugly hack to make this parser happy with double '\t's
        lines = [line.replace("\t\t", "\t") for line in lines]

        # parse rules
        rules = []
        for line in lines:
            rule = []
            tokens = line.split("\t")

            # text to be searched for at the end of the string
            rule.append( tokens[0][1:-1] ) # remove quotes

            # minimum stem size to perform the replacement
            rule.append( int(tokens[1]) )

            # text to be replaced into
            rule.append( tokens[2][1:-1] ) # remove quotes

            # exceptions to this rule
            rule.append( [token[1:-1] for token in tokens[3].split(",")] )

            # append to the results
            rules.append(rule)

        return rules

    def stem(self, word):
        # lower, since all the rules are lower-cased
        word = word.lower()
        # don't stem stopwords
        if word in self.stopwords:
            return word

        # the word ends in 's'? apply rule for plural reduction
        if word[-1] == "s":
            word = self.apply_rule(word, 0)

        # the word ends in 'a'? apply rule for feminine reduction
        if word[-1] == "a":
            word = self.apply_rule(word, 1)

        # augmentative reduction
        word = self.apply_rule(word, 3)

        # adverb reduction
        word = self.apply_rule(word, 2)

        # noun reduction
        prev_word = word
        word = self.apply_rule(word, 4)
        if word == prev_word:
            # verb reduction
            prev_word = word
            word = self.apply_rule(word, 5)
            if word == prev_word:
                # vowel removal
                word = self.apply_rule(word, 6)

        return word

    def apply_rule(self, word, rule_index):
        rules = self._model[rule_index]
        for rule in rules:
            suffix_length = len(rule[0])
            # if suffix matches
            if word[-suffix_length:] == rule[0]:
                # if we have minimum size
                if len(word) >= suffix_length + rule[1]:
                    # if not an exception
                    if word not in rule[3]:
                        word = word[:-suffix_length] + rule[2]
                        break

        return word


class SnowballStemmer(Stemmer):
    """Snowball stemmers

    This module provides a port of the Snowball stemmers
    developed by U{Dr Martin Porter<http://tartarus.org/~martin/>}.
    There is also a demo function demonstrating the different
    algorithms. It can be invoked directly on the command line.
    For more information take a look into the class C{SnowballStemmer}.

    @author: Peter Michael Stahl
    @contact: pemistahl@gmail.com
    @contact: U{http://twitter.com/pemistahl}

    A word stemmer based on the Snowball stemming algorithms.

    At the moment, this port is able to stem words from thirteen
    languages: Danish, Dutch, Finnish, French, German,
    Hungarian, Italian, Norwegian, Portuguese, Romanian, Russian,
    Spanish and Swedish.

    The algorithms have been developed by
    U{Dr Martin Porter<http://tartarus.org/~martin/>}.
    These stemmers are called Snowball, because he invented
    a programming language with this name for creating
    new stemming algorithms. There is more information available
    on the U{Snowball Website<http://snowball.tartarus.org/>}.

    """

    def __init__(self, stopwords=None):
        """Create an instance of the Snowball stemmer."""
        if stopwords is None:
            stopwords = []
        self.stopwords = set(stopwords)


class _StandardStemmer(SnowballStemmer):
    """StandardStemmer

    This subclass encapsulates two methods for defining the standard versions
    of the string regions R1, R2, and RV.

    """

    def _r1r2_standard(self, word, vowels):
        """
        Return the standard interpretations of the string regions R1 and R2.

        R1 is the region after the first non-vowel following a vowel,
        or is the null region at the end of the word if there is no
        such non-vowel.

        R2 is the region after the first non-vowel following a vowel
        in R1, or is the null region at the end of the word if there
        is no such non-vowel.

        @param word: The word whose regions R1 and R2 are determined.
        @type word: C{str, unicode}
        @param vowels: The vowels of the respective language that are
                       used to determine the regions R1 and R2.
        @type vowels: C{unicode}
        @return: C{(r1,r2)}, the regions R1 and R2 for the respective
                 word.
        @rtype: C{tuple}
        @note: This helper method is invoked by the respective stem method of
               the subclasses L{DutchStemmer}, L{FinnishStemmer},
               L{FrenchStemmer}, L{GermanStemmer}, L{ItalianStemmer},
               L{PortugueseStemmer}, L{RomanianStemmer}, and L{SpanishStemmer}.
               It is not to be invoked directly!
        @note: A detailed description of how to define R1 and R2
               can be found under U{http://snowball.tartarus.org/
               texts/r1r2.html}.

        """
        r1 = u""
        r2 = u""
        for i in xrange(1, len(word)):
            if word[i] not in vowels and word[i-1] in vowels:
                r1 = word[i+1:]
                break

        for i in xrange(1, len(r1)):
            if r1[i] not in vowels and r1[i-1] in vowels:
                r2 = r1[i+1:]
                break

        return (r1, r2)

    def _rv_standard(self, word, vowels):
        """
        Return the standard interpretation of the string region RV.

        If the second letter is a consonant, RV is the region after the
        next following vowel. If the first two letters are vowels, RV is
        the region after the next following consonant. Otherwise, RV is
        the region after the third letter.

        @param word: The word whose region RV is determined.
        @type word: C{str, unicode}
        @param vowels: The vowels of the respective language that are
                       used to determine the region RV.
        @type vowels: C{unicode}
        @return: C{rv}, the region RV for the respective word.
        @rtype: C{unicode}
        @note: This helper method is invoked by the respective stem method of
               the subclasses L{ItalianStemmer}, L{PortugueseStemmer},
               L{RomanianStemmer}, and L{SpanishStemmer}. It is not to be
               invoked directly!

        """
        rv = u""
        if len(word) >= 2:
            if word[1] not in vowels:
                for i in xrange(2, len(word)):
                    if word[i] in vowels:
                        rv = word[i+1:]
                        break

            elif word[:2] in vowels:
                for i in xrange(2, len(word)):
                    if word[i] not in vowels:
                        rv = word[i+1:]
                        break
            else:
                rv = word[3:]

        return rv


class _ScandinavianStemmer(SnowballStemmer):
    """ScandinavianStemmer
    This subclass encapsulates a method for defining the string region R1.
    It is used by the Danish, Norwegian, and Swedish stemmer.

    """

    def _r1_scandinavian(self, word, vowels):
        """
        Return the region R1 that is used by the Scandinavian stemmers.

        R1 is the region after the first non-vowel following a vowel,
        or is the null region at the end of the word if there is no
        such non-vowel. But then R1 is adjusted so that the region
        before it contains at least three letters.

        @param word: The word whose region R1 is determined.
        @type word: C{str, unicode}
        @param vowels: The vowels of the respective language that are
                       used to determine the region R1.
        @type vowels: C{unicode}
        @return: C{r1}, the region R1 for the respective word.
        @rtype: C{unicode}
        @note: This helper method is invoked by the respective stem method of
               the subclasses L{DanishStemmer}, L{NorwegianStemmer}, and
               L{SwedishStemmer}. It is not to be invoked directly!

        """
        r1 = u""
        for i in xrange(1, len(word)):
            if word[i] not in vowels and word[i-1] in vowels:
                if len(word[:i+1]) < 3 and len(word[:i+1]) > 0:
                    r1 = word[3:]
                elif len(word[:i+1]) >= 3:
                    r1 = word[i+1:]
                else:
                    return word
                break

        return r1


class DanishStemmer(_ScandinavianStemmer):
    """The Danish Snowball stemmer.

    @cvar __vowels: The Danish vowels.
    @type __vowels: C{unicode}
    @cvar __consonants: The Danish consonants.
    @type __consonants: C{unicode}
    @cvar __double_consonants: The Danish double consonants.
    @type __double_consonants: C{tuple}
    @cvar __s_ending: Letters that may directly appear before a word final 's'.
    @type __s_ending: C{unicode}
    @cvar __step1_suffixes: Suffixes to be deleted in step 1 of the algorithm.
    @type __step1_suffixes: C{tuple}
    @cvar __step2_suffixes: Suffixes to be deleted in step 2 of the algorithm.
    @type __step2_suffixes: C{tuple}
    @cvar __step3_suffixes: Suffixes to be deleted in step 3 of the algorithm.
    @type __step3_suffixes: C{tuple}
    @note: A detailed description of the Danish
           stemming algorithm can be found under
           U{http://snowball.tartarus.org/algorithms
           /danish/stemmer.html}.

    """

    zope.interface.implements(interfaces.IDanishStemmer)

    # The language's vowels and other important characters are defined.
    __vowels = u"aeiouy\xE6\xE5\xF8"
    __consonants = u"bcdfghjklmnpqrstvwxz"
    __double_consonants = (u"bb", u"cc", u"dd", u"ff", u"gg", u"hh", u"jj",
                           u"kk", u"ll", u"mm", u"nn", u"pp", u"qq", u"rr",
                           u"ss", u"tt", u"vv", u"ww", u"xx", u"zz")
    __s_ending = u"abcdfghjklmnoprtvyz\xE5"

    # The different suffixes, divided into the algorithm's steps
    # and organized by length, are listed in tuples.
    __step1_suffixes = (u"erendes", u"erende", u"hedens", u"ethed", 
                        u"erede", u"heden", u"heder", u"endes", 
                        u"ernes", u"erens", u"erets", u"ered", 
                        u"ende", u"erne", u"eren", u"erer", u"heds", 
                        u"enes", u"eres", u"eret", u"hed", u"ene", u"ere", 
                        u"ens", u"ers", u"ets", u"en", u"er", u"es", u"et", 
                        u"e", u"s")
    __step2_suffixes = (u"gd", u"dt", u"gt", u"kt")
    __step3_suffixes = (u"elig", u"l\xF8st", u"lig", u"els", u"ig")

    def stem(self, word):
        """
        Stem a Danish word and return the stemmed form.

        @param word: The word that is stemmed.
        @type word: C{str, unicode}
        @return: The stemmed form.
        @rtype: C{unicode}

        """
        # lower, since all the rules are lower-cased
        word = word.lower()
        # don't stem stopwords
        if word in self.stopwords:
            return word

        # After this, the required regions are generated
        # by the respective helper method.
        r1 = self._r1_scandinavian(word, self.__vowels)

        # Then the actual stemming process starts.
        # Every new step is explicitly indicated
        # according to the descriptions on the Snowball website.

        # STEP 1
        for suffix in self.__step1_suffixes:
            if r1.endswith(suffix):
                if suffix == u"s":
                    if word[-2] in self.__s_ending:
                        word = word[:-1]
                        r1 = r1[:-1]
                else:
                    word = word[:-len(suffix)]
                    r1 = r1[:-len(suffix)]
                break

        # STEP 2
        for suffix in self.__step2_suffixes:
            if r1.endswith(suffix):
                word = word[:-1]
                r1 = r1[:-1]
                break

        # STEP 3
        if r1.endswith(u"igst"):
            word = word[:-2]
            r1 = r1[:-2]

        for suffix in self.__step3_suffixes:
            if r1.endswith(suffix):
                if suffix == u"l\xF8st":
                    word = word[:-1]
                    r1 = r1[:-1]
                else:
                    word = word[:-len(suffix)]
                    r1 = r1[:-len(suffix)]

                    if r1.endswith(self.__step2_suffixes):
                        word = word[:-1]
                        r1 = r1[:-1]
                break

        # STEP 4: Undouble
        for double_cons in self.__double_consonants:
            if word.endswith(double_cons) and len(word) > 3:
                word = word[:-1]
                break


        return word


class DutchStemmer(_StandardStemmer):
    """The Dutch Snowball stemmer.

    @cvar __vowels: The Dutch vowels.
    @type __vowels: C{unicode}
    @cvar __step1_suffixes: Suffixes to be deleted in step 1 of the algorithm.
    @type __step1_suffixes: C{tuple}
    @cvar __step3b_suffixes: Suffixes to be deleted in step 3b of the algorithm.
    @type __step3b_suffixes: C{tuple}
    @note: A detailed description of the Dutch
           stemming algorithm can be found under
           U{http://snowball.tartarus.org/algorithms
           /dutch/stemmer.html}.

    """

    zope.interface.implements(interfaces.IDutchStemmer)

    __vowels = u"aeiouy\xE8"
    __step1_suffixes = (u"heden", u"ene", u"en", u"se", u"s")
    __step3b_suffixes = (u"baar", u"lijk", u"bar", u"end", u"ing", u"ig")

    def stem(self, word):
        """
        Stem a Dutch word and return the stemmed form.

        @param word: The word that is stemmed.
        @type word: C{str, unicode}
        @return: The stemmed form.
        @rtype: C{unicode}

        """
        # lower, since all the rules are lower-cased
        word = word.lower()
        # don't stem stopwords
        if word in self.stopwords:
            return word

        step2_success = False

        # Vowel accents are removed.
        word = (word.replace(u"\xE4", u"a").replace(u"\xE1", u"a")
                    .replace(u"\xEB", u"e").replace(u"\xE9", u"e")
                    .replace(u"\xED", u"i").replace(u"\xEF", u"i")
                    .replace(u"\xF6", u"o").replace(u"\xF3", u"o")
                    .replace(u"\xFC", u"u").replace(u"\xFA", u"u"))

        # An initial 'y', a 'y' after a vowel,
        # and an 'i' between self.__vowels is put into upper case.
        # As from now these are treated as consonants.
        if word.startswith(u"y"):
            word = u"".join((u"Y", word[1:]))

        for i in xrange(1, len(word)):
            if word[i-1] in self.__vowels and word[i] == u"y":
                word = u"".join((word[:i], u"Y", word[i+1:]))

        for i in xrange(1, len(word)-1):
            if (word[i-1] in self.__vowels and word[i] == u"i" and
               word[i+1] in self.__vowels):
                word = u"".join((word[:i], u"I", word[i+1:]))

        r1, r2 = self._r1r2_standard(word, self.__vowels)

        # R1 is adjusted so that the region before it
        # contains at least 3 letters.
        for i in xrange(1, len(word)):
            if word[i] not in self.__vowels and word[i-1] in self.__vowels:
                if len(word[:i+1]) < 3 and len(word[:i+1]) > 0:
                    r1 = word[3:]
                elif len(word[:i+1]) == 0:
                    return word
                break

        # STEP 1
        for suffix in self.__step1_suffixes:
            if r1.endswith(suffix):
                if suffix == u"heden":
                    word = u"".join((word[:-5], u"heid"))
                    r1 = u"".join((r1[:-5], u"heid"))
                    if r2.endswith(u"heden"):
                        r2 = u"".join((r2[:-5], u"heid"))

                elif (suffix in (u"ene", u"en") and
                      not word.endswith(u"heden") and
                      word[-len(suffix)-1] not in self.__vowels and
                      word[-len(suffix)-3:-len(suffix)] != u"gem"):
                    word = word[:-len(suffix)]
                    r1 = r1[:-len(suffix)]
                    r2 = r2[:-len(suffix)]
                    if word.endswith((u"kk", u"dd", u"tt")):
                        word = word[:-1]
                        r1 = r1[:-1]
                        r2 = r2[:-1]

                elif (suffix in (u"se", u"s") and
                      word[-len(suffix)-1] not in self.__vowels and
                      word[-len(suffix)-1] != u"j"):
                    word = word[:-len(suffix)]
                    r1 = r1[:-len(suffix)]
                    r2 = r2[:-len(suffix)]
                break

        # STEP 2
        if r1.endswith(u"e") and word[-2] not in self.__vowels:
            step2_success = True
            word = word[:-1]
            r1 = r1[:-1]
            r2 = r2[:-1]

            if word.endswith((u"kk", u"dd", u"tt")):
                word = word[:-1]
                r1 = r1[:-1]
                r2 = r2[:-1]

        # STEP 3a
        if r2.endswith(u"heid") and word[-5] != u"c":
            word = word[:-4]
            r1 = r1[:-4]
            r2 = r2[:-4]

            if (r1.endswith(u"en") and word[-3] not in self.__vowels and
                word[-5:-2] != u"gem"):
                word = word[:-2]
                r1 = r1[:-2]
                r2 = r2[:-2]

                if word.endswith((u"kk", u"dd", u"tt")):
                    word = word[:-1]
                    r1 = r1[:-1]
                    r2 = r2[:-1]

        # STEP 3b: Derivational suffixes
        for suffix in self.__step3b_suffixes:
            if r2.endswith(suffix):
                if suffix in (u"end", u"ing"):
                    word = word[:-3]
                    r2 = r2[:-3]

                    if r2.endswith(u"ig") and word[-3] != u"e":
                        word = word[:-2]
                    else:
                        if word.endswith((u"kk", u"dd", u"tt")):
                            word = word[:-1]

                elif suffix == u"ig" and word[-3] != u"e":
                    word = word[:-2]

                elif suffix == u"lijk":
                    word = word[:-4]
                    r1 = r1[:-4]

                    if r1.endswith(u"e") and word[-2] not in self.__vowels:
                        word = word[:-1]
                        if word.endswith((u"kk", u"dd", u"tt")):
                            word = word[:-1]

                elif suffix == u"baar":
                    word = word[:-4]

                elif suffix == u"bar" and step2_success:
                    word = word[:-3]
                break

        # STEP 4: Undouble vowel
        if len(word) >= 4:
            if word[-1] not in self.__vowels and word[-1] != u"I":
                if word[-3:-1] in (u"aa", u"ee", u"oo", u"uu"):
                    if word[-4] not in self.__vowels:
                        word = u"".join((word[:-3], word[-3], word[-1]))

        # All occurrences of 'I' and 'Y' are put back into lower case.
        word = word.replace(u"I", u"i").replace(u"Y", u"y")


        return word


class FinnishStemmer(_StandardStemmer):
    """The Finnish Snowball stemmer.

    @cvar __vowels: The Finnish vowels.
    @type __vowels: C{unicode}
    @cvar __restricted_vowels: A subset of the Finnish vowels.
    @type __restricted_vowels: C{unicode}
    @cvar __long_vowels: The Finnish vowels in their long forms.
    @type __long_vowels: C{tuple}
    @cvar __consonants: The Finnish consonants.
    @type __consonants: C{unicode}
    @cvar __double_consonants: The Finnish double consonants.
    @type __double_consonants: C{tuple}
    @cvar __step1_suffixes: Suffixes to be deleted in step 1 of the algorithm.
    @type __step1_suffixes: C{tuple}
    @cvar __step2_suffixes: Suffixes to be deleted in step 2 of the algorithm.
    @type __step2_suffixes: C{tuple}
    @cvar __step3_suffixes: Suffixes to be deleted in step 3 of the algorithm.
    @type __step3_suffixes: C{tuple}
    @cvar __step4_suffixes: Suffixes to be deleted in step 4 of the algorithm.
    @type __step4_suffixes: C{tuple}
    @note: A detailed description of the Finnish
           stemming algorithm can be found under
           U{http://snowball.tartarus.org/algorithms
           /finnish/stemmer.html}.

    """

    zope.interface.implements(interfaces.IFinnishStemmer)

    __vowels = u"aeiouy\xE4\xF6"
    __restricted_vowels = u"aeiou\xE4\xF6"
    __long_vowels = (u"aa", u"ee", u"ii", u"oo", u"uu", u"\xE4\xE4",
                     u"\xF6\xF6")
    __consonants = u"bcdfghjklmnpqrstvwxz"
    __double_consonants = (u"bb", u"cc", u"dd", u"ff", u"gg", u"hh", u"jj",
                           u"kk", u"ll", u"mm", u"nn", u"pp", u"qq", u"rr",
                           u"ss", u"tt", u"vv", u"ww", u"xx", u"zz")
    __step1_suffixes = (u'kaan', u'k\xE4\xE4n', u'sti', u'kin', u'han',
                        u'h\xE4n', u'ko', u'k\xF6', u'pa', u'p\xE4')
    __step2_suffixes = (u'nsa', u'ns\xE4', u'mme', u'nne', u'si', u'ni', 
                        u'an', u'\xE4n', u'en')
    __step3_suffixes = (u'siin', u'tten', u'seen', u'han', u'hen', u'hin', 
                        u'hon', u'h\xE4n', u'h\xF6n', u'den', u'tta', 
                        u'tt\xE4', u'ssa', u'ss\xE4', u'sta', 
                        u'st\xE4', u'lla', u'll\xE4', u'lta', 
                        u'lt\xE4', u'lle', u'ksi', u'ine', u'ta', 
                        u't\xE4', u'na', u'n\xE4', u'a', u'\xE4', 
                        u'n')
    __step4_suffixes = (u'impi', u'impa', u'imp\xE4', u'immi', u'imma',
                        u'imm\xE4', u'mpi', u'mpa', u'mp\xE4', u'mmi',
                        u'mma', u'mm\xE4', u'eja', u'ej\xE4')

    def stem(self, word):
        """
        Stem a Finnish word and return the stemmed form.

        @param word: The word that is stemmed.
        @type word: C{str, unicode}
        @return: The stemmed form.
        @rtype: C{unicode}

        """
        # lower, since all the rules are lower-cased
        word = word.lower()
        # don't stem stopwords
        if word in self.stopwords:
            return word

        step3_success = False

        r1, r2 = self._r1r2_standard(word, self.__vowels)

        # STEP 1: Particles etc.
        for suffix in self.__step1_suffixes:
            if r1.endswith(suffix):
                if suffix == u"sti":
                    if suffix in r2:
                        word = word[:-3]
                        r1 = r1[:-3]
                        r2 = r2[:-3]
                else:
                    if word[-len(suffix)-1] in u"ntaeiouy\xE4\xF6":
                        word = word[:-len(suffix)]
                        r1 = r1[:-len(suffix)]
                        r2 = r2[:-len(suffix)]
                break

        # STEP 2: Possessives
        for suffix in self.__step2_suffixes:
            if r1.endswith(suffix):
                if suffix == u"si":
                    if word[-3] != u"k":
                        word = word[:-2]
                        r1 = r1[:-2]
                        r2 = r2[:-2]

                elif suffix == u"ni":
                    word = word[:-2]
                    r1 = r1[:-2]
                    r2 = r2[:-2]
                    if word.endswith(u"kse"):
                        word = u"".join((word[:-3], u"ksi"))

                    if r1.endswith(u"kse"):
                        r1 = u"".join((r1[:-3], u"ksi"))

                    if r2.endswith(u"kse"):
                        r2 = u"".join((r2[:-3], u"ksi"))

                elif suffix == u"an":
                    if (word[-4:-2] in (u"ta", u"na") or
                        word[-5:-2] in (u"ssa", u"sta", u"lla", u"lta")):
                        word = word[:-2]
                        r1 = r1[:-2]
                        r2 = r2[:-2]

                elif suffix == u"\xE4n":
                    if (word[-4:-2] in (u"t\xE4", u"n\xE4") or
                        word[-5:-2] in (u"ss\xE4", u"st\xE4",
                                        u"ll\xE4", u"lt\xE4")):
                        word = word[:-2]
                        r1 = r1[:-2]
                        r2 = r2[:-2]

                elif suffix == u"en":
                    if word[-5:-2] in (u"lle", u"ine"):
                        word = word[:-2]
                        r1 = r1[:-2]
                        r2 = r2[:-2]
                else:
                    word = word[:-3]
                    r1 = r1[:-3]
                    r2 = r2[:-3]
                break

        # STEP 3: Cases
        for suffix in self.__step3_suffixes:
            if r1.endswith(suffix):
                if suffix in (u"han", u"hen", u"hin", u"hon", u"h\xE4n",
                              u"h\xF6n"):
                    if ((suffix == u"han" and word[-4] == u"a") or
                        (suffix == u"hen" and word[-4] == u"e") or
                        (suffix == u"hin" and word[-4] == u"i") or
                        (suffix == u"hon" and word[-4] == u"o") or
                        (suffix == u"h\xE4n" and word[-4] == u"\xE4") or
                        (suffix == u"h\xF6n" and word[-4] == u"\xF6")):
                        word = word[:-3]
                        r1 = r1[:-3]
                        r2 = r2[:-3]
                        step3_success = True

                elif suffix in (u"siin", u"den", u"tten"):
                    if (word[-len(suffix)-1] == u"i" and
                        word[-len(suffix)-2] in self.__restricted_vowels):
                        word = word[:-len(suffix)]
                        r1 = r1[:-len(suffix)]
                        r2 = r2[:-len(suffix)]
                        step3_success = True
                    else:
                        continue

                elif suffix == u"seen":
                    if word[-6:-4] in self.__long_vowels:
                        word = word[:-4]
                        r1 = r1[:-4]
                        r2 = r2[:-4]
                        step3_success = True
                    else:
                        continue

                elif suffix in (u"a", u"\xE4"):
                    if word[-2] in self.__vowels and word[-3] in self.__consonants:
                        word = word[:-1]
                        r1 = r1[:-1]
                        r2 = r2[:-1]
                        step3_success = True

                elif suffix in (u"tta", u"tt\xE4"):
                    if word[-4] == u"e":
                        word = word[:-3]
                        r1 = r1[:-3]
                        r2 = r2[:-3]
                        step3_success = True

                elif suffix == u"n":
                    word = word[:-1]
                    r1 = r1[:-1]
                    r2 = r2[:-1]
                    step3_success = True

                    if word[-2:] == u"ie" or word[-2:] in self.__long_vowels:
                        word = word[:-1]
                        r1 = r1[:-1]
                        r2 = r2[:-1]
                else:
                    word = word[:-len(suffix)]
                    r1 = r1[:-len(suffix)]
                    r2 = r2[:-len(suffix)]
                    step3_success = True
                break

        # STEP 4: Other endings
        for suffix in self.__step4_suffixes:
            if r2.endswith(suffix):
                if suffix in (u"mpi", u"mpa", u"mp\xE4", u"mmi", u"mma",
                              u"mm\xE4"):
                    if word[-5:-3] != u"po":
                        word = word[:-3]
                        r1 = r1[:-3]
                        r2 = r2[:-3]
                else:
                    word = word[:-len(suffix)]
                    r1 = r1[:-len(suffix)]
                    r2 = r2[:-len(suffix)]
                break

        # STEP 5: Plurals
        if step3_success and len(r1) >= 1 and r1[-1] in u"ij":
            word = word[:-1]
            r1 = r1[:-1]

        elif (not step3_success and len(r1) >= 2 and
              r1[-1] == u"t" and r1[-2] in self.__vowels):
            word = word[:-1]
            r1 = r1[:-1]
            r2 = r2[:-1]
            if r2.endswith(u"imma"):
                word = word[:-4]
                r1 = r1[:-4]
            elif r2.endswith(u"mma") and r2[-5:-3] != u"po":
                word = word[:-3]
                r1 = r1[:-3]

        # STEP 6: Tidying up
        if r1[-2:] in self.__long_vowels:
            word = word[:-1]
            r1 = r1[:-1]

        if (len(r1) >= 2 and r1[-2] in self.__consonants and
            r1[-1] in u"a\xE4ei"):
            word = word[:-1]
            r1 = r1[:-1]

        if r1.endswith((u"oj", u"uj")):
            word = word[:-1]
            r1 = r1[:-1]

        if r1.endswith(u"jo"):
            word = word[:-1]
            r1 = r1[:-1]

        # If the word ends with a double consonant
        # followed by zero or more vowels, the last consonant is removed.
        for i in xrange(1, len(word)):
            if word[-i] in self.__vowels:
                continue
            else:
                if i == 1:
                    if word[-i-1:] in self.__double_consonants:
                        word = word[:-1]
                else:
                    if word[-i-1:-i+1] in self.__double_consonants:
                        word = u"".join((word[:-i], word[-i+1:]))
                break


        return word


class FrenchStemmer(_StandardStemmer):
    """The French Snowball stemmer.

    @cvar __vowels: The French vowels.
    @type __vowels: C{unicode}
    @cvar __step1_suffixes: Suffixes to be deleted in step 1 of the algorithm.
    @type __step1_suffixes: C{tuple}
    @cvar __step2a_suffixes: Suffixes to be deleted in step 2a of the algorithm.
    @type __step2a_suffixes: C{tuple}
    @cvar __step2b_suffixes: Suffixes to be deleted in step 2b of the algorithm.
    @type __step2b_suffixes: C{tuple}
    @cvar __step4_suffixes: Suffixes to be deleted in step 4 of the algorithm.
    @type __step4_suffixes: C{tuple}
    @note: A detailed description of the French
           stemming algorithm can be found under
           U{http://snowball.tartarus.org/algorithms
           /french/stemmer.html}.

    """

    zope.interface.implements(interfaces.IFrenchStemmer)

    __vowels = u"aeiouy\xE2\xE0\xEB\xE9\xEA\xE8\xEF\xEE\xF4\xFB\xF9"
    __step1_suffixes = (u'issements', u'issement', u'atrices', u'atrice',
                        u'ateurs', u'ations', u'logies', u'usions', 
                        u'utions', u'ements', u'amment', u'emment', 
                        u'ances', u'iqUes', u'ismes', u'ables', u'istes', 
                        u'ateur', u'ation', u'logie', u'usion', u'ution', 
                        u'ences', u'ement', u'euses', u'ments', u'ance', 
                        u'iqUe', u'isme', u'able', u'iste', u'ence', 
                        u'it\xE9s', u'ives', u'eaux', u'euse', u'ment', 
                        u'eux', u'it\xE9', u'ive', u'ifs', u'aux', u'if')
    __step2a_suffixes = (u'issaIent', u'issantes', u'iraIent', u'issante',
                         u'issants', u'issions', u'irions', u'issais', 
                         u'issait', u'issant', u'issent', u'issiez', u'issons', 
                         u'irais', u'irait', u'irent', u'iriez', u'irons', 
                         u'iront', u'isses', u'issez', u'\xEEmes', 
                         u'\xEEtes', u'irai', u'iras', u'irez', u'isse', 
                         u'ies', u'ira', u'\xEEt', u'ie', u'ir', u'is', 
                         u'it', u'i')
    __step2b_suffixes = (u'eraIent', u'assions', u'erions', u'assent', 
                         u'assiez', u'\xE8rent', u'erais', u'erait', 
                         u'eriez', u'erons', u'eront', u'aIent', u'antes', 
                         u'asses', u'ions', u'erai', u'eras', u'erez', 
                         u'\xE2mes', u'\xE2tes', u'ante', u'ants', 
                         u'asse', u'\xE9es', u'era', u'iez', u'ais', 
                         u'ait', u'ant', u'\xE9e', u'\xE9s', u'er', 
                         u'ez', u'\xE2t', u'ai', u'as', u'\xE9', u'a')
    __step4_suffixes = (u'i\xE8re', u'I\xE8re', u'ion', u'ier', u'Ier', 
                        u'e', u'\xEB')

    def stem(self, word):
        """
        Stem a French word and return the stemmed form.

        @param word: The word that is stemmed.
        @type word: C{str, unicode}
        @return: The stemmed form.
        @rtype: C{unicode}

        """
        # lower, since all the rules are lower-cased
        word = word.lower()
        # don't stem stopwords
        if word in self.stopwords:
            return word

        step1_success = False
        rv_ending_found = False
        step2a_success = False
        step2b_success = False

        # Every occurrence of 'u' after 'q' is put into upper case.
        for i in xrange(1, len(word)):
            if word[i-1] == u"q" and word[i] == u"u":
                word = u"".join((word[:i], u"U", word[i+1:]))

        # Every occurrence of 'u' and 'i'
        # between vowels is put into upper case.
        # Every occurrence of 'y' preceded or
        # followed by a vowel is also put into upper case.
        for i in xrange(1, len(word)-1):
            if word[i-1] in self.__vowels and word[i+1] in self.__vowels:
                if word[i] == u"u":
                    word = u"".join((word[:i], u"U", word[i+1:]))

                elif word[i] == u"i":
                    word = u"".join((word[:i], u"I", word[i+1:]))

            if word[i-1] in self.__vowels or word[i+1] in self.__vowels:
                if word[i] == u"y":
                    word = u"".join((word[:i], u"Y", word[i+1:]))

        r1, r2 = self._r1r2_standard(word, self.__vowels)
        rv = self.__rv_french(word, self.__vowels)

        # STEP 1: Standard suffix removal
        for suffix in self.__step1_suffixes:
            if word.endswith(suffix):
                if suffix == u"eaux":
                    word = word[:-1]
                    step1_success = True

                elif suffix in (u"euse", u"euses"):
                    if suffix in r2:
                        word = word[:-len(suffix)]
                        step1_success = True

                    elif suffix in r1:
                        word = u"".join((word[:-len(suffix)], u"eux"))
                        step1_success = True

                elif suffix in (u"ement", u"ements") and suffix in rv:
                    word = word[:-len(suffix)]
                    step1_success = True

                    if word[-2:] == u"iv" and u"iv" in r2:
                        word = word[:-2]

                        if word[-2:] == u"at" and u"at" in r2:
                            word = word[:-2]

                    elif word[-3:] == u"eus":
                        if u"eus" in r2:
                            word = word[:-3]
                        elif u"eus" in r1:
                            word = u"".join((word[:-1], u"x"))

                    elif word[-3:] in (u"abl", u"iqU"):
                        if u"abl" in r2 or u"iqU" in r2:
                            word = word[:-3]

                    elif word[-3:] in (u"i\xE8r", u"I\xE8r"):
                        if u"i\xE8r" in rv or u"I\xE8r" in rv:
                            word = u"".join((word[:-3], u"i"))

                elif suffix == u"amment" and suffix in rv:
                    word = u"".join((word[:-6], u"ant"))
                    rv = u"".join((rv[:-6], u"ant"))
                    rv_ending_found = True

                elif suffix == u"emment" and suffix in rv:
                    word = u"".join((word[:-6], u"ent"))
                    rv_ending_found = True

                elif (suffix in (u"ment", u"ments") and suffix in rv and
                      not rv.startswith(suffix) and
                      rv[rv.rindex(suffix)-1] in self.__vowels):
                    word = word[:-len(suffix)]
                    rv = rv[:-len(suffix)]
                    rv_ending_found = True

                elif suffix == u"aux" and suffix in r1:
                    word = u"".join((word[:-2], u"l"))
                    step1_success = True

                elif (suffix in (u"issement", u"issements") and suffix in r1
                      and word[-len(suffix)-1] not in self.__vowels):
                    word = word[:-len(suffix)]
                    step1_success = True

                elif suffix in (u"ance", u"iqUe", u"isme", u"able", u"iste",
                              u"eux", u"ances", u"iqUes", u"ismes",
                              u"ables", u"istes") and suffix in r2:
                    word = word[:-len(suffix)]
                    step1_success = True

                elif suffix in (u"atrice", u"ateur", u"ation", u"atrices",
                                u"ateurs", u"ations") and suffix in r2:
                    word = word[:-len(suffix)]
                    step1_success = True

                    if word[-2:] == u"ic":
                        if u"ic" in r2:
                            word = word[:-2]
                        else:
                            word = u"".join((word[:-2], u"iqU"))

                elif suffix in (u"logie", u"logies") and suffix in r2:
                    word = u"".join((word[:-len(suffix)], u"log"))
                    step1_success = True

                elif (suffix in (u"usion", u"ution", u"usions", u"utions") and
                      suffix in r2):
                    word = u"".join((word[:-len(suffix)], u"u"))
                    step1_success = True

                elif suffix in (u"ence", u"ences") and suffix in r2:
                    word = u"".join((word[:-len(suffix)], u"ent"))
                    step1_success = True

                elif suffix in (u"it\xE9", u"it\xE9s") and suffix in r2:
                    word = word[:-len(suffix)]
                    step1_success = True

                    if word[-4:] == u"abil":
                        if u"abil" in r2:
                            word = word[:-4]
                        else:
                            word = u"".join((word[:-2], u"l"))

                    elif word[-2:] == u"ic":
                        if u"ic" in r2:
                            word = word[:-2]
                        else:
                            word = u"".join((word[:-2], u"iqU"))

                    elif word[-2:] == u"iv":
                        if u"iv" in r2:
                            word = word[:-2]

                elif (suffix in (u"if", u"ive", u"ifs", u"ives") and 
                      suffix in r2):
                    word = word[:-len(suffix)]
                    step1_success = True

                    if word[-2:] == u"at" and u"at" in r2:
                        word = word[:-2]

                        if word[-2:] == u"ic":
                            if u"ic" in r2:
                                word = word[:-2]
                            else:
                                word = u"".join((word[:-2], u"iqU"))
                break

        # STEP 2a: Verb suffixes beginning 'i'
        if not step1_success or rv_ending_found:
            for suffix in self.__step2a_suffixes:
                if word.endswith(suffix):
                    if (suffix in rv and len(rv) > len(suffix) and
                        rv[rv.rindex(suffix)-1] not in self.__vowels):
                        word = word[:-len(suffix)]
                        step2a_success = True
                    break

        # STEP 2b: Other verb suffixes
            if not step2a_success:
                for suffix in self.__step2b_suffixes:
                    if rv.endswith(suffix):
                        if suffix == u"ions" and u"ions" in r2:
                            word = word[:-4]
                            step2b_success = True

                        elif suffix in (u'eraIent', u'erions', u'\xE8rent',
                                        u'erais', u'erait', u'eriez', 
                                        u'erons', u'eront', u'erai', u'eras', 
                                        u'erez', u'\xE9es', u'era', u'iez', 
                                        u'\xE9e', u'\xE9s', u'er', u'ez', 
                                        u'\xE9'):
                            word = word[:-len(suffix)]
                            step2b_success = True

                        elif suffix in (u'assions', u'assent', u'assiez',
                                        u'aIent', u'antes', u'asses',
                                        u'\xE2mes', u'\xE2tes', u'ante',
                                        u'ants', u'asse', u'ais', u'ait', 
                                        u'ant', u'\xE2t', u'ai', u'as', 
                                        u'a'):
                            word = word[:-len(suffix)]
                            rv = rv[:-len(suffix)]
                            step2b_success = True
                            if rv.endswith(u"e"):
                                word = word[:-1]
                        break

        # STEP 3
        if step1_success or step2a_success or step2b_success:
            if word[-1] == u"Y":
                word = u"".join((word[:-1], u"i"))
            elif word[-1] == u"\xE7":
                word = u"".join((word[:-1], u"c"))

        # STEP 4: Residual suffixes
        else:
            if (len(word) >= 2 and word[-1] == u"s" and
                word[-2] not in u"aiou\xE8s"):
                word = word[:-1]

            for suffix in self.__step4_suffixes:
                if word.endswith(suffix):
                    if suffix in rv:
                        if (suffix == u"ion" and suffix in r2 and
                            rv[-4] in u"st"):
                            word = word[:-3]

                        elif suffix in (u"ier", u"i\xE8re", u"Ier",
                                        u"I\xE8re"):
                            word = u"".join((word[:-len(suffix)], u"i"))

                        elif suffix == u"e":
                            word = word[:-1]

                        elif suffix == u"\xEB" and word[-3:-1] == u"gu":
                            word = word[:-1]
                        break

        # STEP 5: Undouble
        if word.endswith((u"enn", u"onn", u"ett", u"ell", u"eill")):
            word = word[:-1]

        # STEP 6: Un-accent
        for i in xrange(1, len(word)):
            if word[-i] not in self.__vowels:
                i += 1
            else:
                if i != 1 and word[-i] in (u"\xE9", u"\xE8"):
                    word = u"".join((word[:-i], u"e", word[-i+1:]))
                break

        word = (word.replace(u"I", u"i")
                    .replace(u"U", u"u")
                    .replace(u"Y", u"y"))


        return word


    def __rv_french(self, word, vowels):
        """
        Return the region RV that is used by the French stemmer.

        If the word begins with two vowels, RV is the region after
        the third letter. Otherwise, it is the region after the first
        vowel not at the beginning of the word, or the end of the word
        if these positions cannot be found. (Exceptionally, u'par',
        u'col' or u'tap' at the beginning of a word is also taken to
        define RV as the region to their right.)

        @param word: The French word whose region RV is determined.
        @type word: C{str, unicode}
        @param vowels: The French vowels that are used to determine
                       the region RV.
        @type vowels: C{unicode}
        @return: C{rv}, the region RV for the respective French word.
        @rtype: C{unicode}
        @note: This helper method is invoked by the stem method of
               the subclass L{FrenchStemmer}. It is not to be invoked directly!

        """
        rv = u""
        if len(word) >= 2:
            if (word.startswith((u"par", u"col", u"tap")) or
                (word[0] in vowels and word[1] in vowels)):
                rv = word[3:]
            else:
                for i in xrange(1, len(word)):
                    if word[i] in vowels:
                        rv = word[i+1:]
                        break

        return rv


class GermanStemmer(_StandardStemmer):
    """The German Snowball stemmer.

    @cvar __vowels: The German vowels.
    @type __vowels: C{unicode}
    @cvar __s_ending: Letters that may directly appear before a word final 's'.
    @type __s_ending: C{unicode}
    @cvar __st_ending: Letter that may directly appear before a word final 'st'.
    @type __st_ending: C{unicode}
    @cvar __step1_suffixes: Suffixes to be deleted in step 1 of the algorithm.
    @type __step1_suffixes: C{tuple}
    @cvar __step2_suffixes: Suffixes to be deleted in step 2 of the algorithm.
    @type __step2_suffixes: C{tuple}
    @cvar __step3_suffixes: Suffixes to be deleted in step 3 of the algorithm.
    @type __step3_suffixes: C{tuple}
    @note: A detailed description of the German
           stemming algorithm can be found under
           U{http://snowball.tartarus.org/algorithms
           /german/stemmer.html}.

    """

    zope.interface.implements(interfaces.IGermanStemmer)

    __vowels = u"aeiouy\xE4\xF6\xFC"
    __s_ending = u"bdfghklmnrt"
    __st_ending = u"bdfghklmnt"

    __step1_suffixes = (u"ern", u"em", u"er", u"en", u"es", u"e", u"s")
    __step2_suffixes = (u"est", u"en", u"er", u"st")
    __step3_suffixes = (u"isch", u"lich", u"heit", u"keit",
                          u"end", u"ung", u"ig", u"ik")

    def stem(self, word):
        """
        Stem a German word and return the stemmed form.

        @param word: The word that is stemmed.
        @type word: C{str, unicode}
        @return: The stemmed form.
        @rtype: C{unicode}

        """
        # lower, since all the rules are lower-cased
        word = word.lower()
        # don't stem stopwords
        if word in self.stopwords:
            return word

        word = word.replace(u"\xDF", u"ss")

        # Every occurrence of 'u' and 'y'
        # between vowels is put into upper case.
        for i in xrange(1, len(word)-1):
            if word[i-1] in self.__vowels and word[i+1] in self.__vowels:
                if word[i] == u"u":
                    word = u"".join((word[:i], u"U", word[i+1:]))

                elif word[i] == u"y":
                    word = u"".join((word[:i], u"Y", word[i+1:]))

        r1, r2 = self._r1r2_standard(word, self.__vowels)

        # R1 is adjusted so that the region before it
        # contains at least 3 letters.
        for i in xrange(1, len(word)):
            if word[i] not in self.__vowels and word[i-1] in self.__vowels:
                if len(word[:i+1]) < 3 and len(word[:i+1]) > 0:
                    r1 = word[3:]
                elif len(word[:i+1]) == 0:
                    return word
                break

        # STEP 1
        for suffix in self.__step1_suffixes:
            if r1.endswith(suffix):
                if (suffix in (u"en", u"es", u"e") and
                    word[-len(suffix)-4:-len(suffix)] == u"niss"):
                    word = word[:-len(suffix)-1]
                    r1 = r1[:-len(suffix)-1]
                    r2 = r2[:-len(suffix)-1]

                elif suffix == u"s":
                    if word[-2] in self.__s_ending:
                        word = word[:-1]
                        r1 = r1[:-1]
                        r2 = r2[:-1]
                else:
                    word = word[:-len(suffix)]
                    r1 = r1[:-len(suffix)]
                    r2 = r2[:-len(suffix)]
                break

        # STEP 2
        for suffix in self.__step2_suffixes:
            if r1.endswith(suffix):
                if suffix == u"st":
                    if word[-3] in self.__st_ending and len(word[:-3]) >= 3:
                        word = word[:-2]
                        r1 = r1[:-2]
                        r2 = r2[:-2]
                else:
                    word = word[:-len(suffix)]
                    r1 = r1[:-len(suffix)]
                    r2 = r2[:-len(suffix)]
                break

        # STEP 3: Derivational suffixes
        for suffix in self.__step3_suffixes:
            if r2.endswith(suffix):
                if suffix in (u"end", u"ung"):
                    if (u"ig" in r2[-len(suffix)-2:-len(suffix)] and
                        u"e" not in r2[-len(suffix)-3:-len(suffix)-2]):
                        word = word[:-len(suffix)-2]
                    else:
                        word = word[:-len(suffix)]

                elif (suffix in (u"ig", u"ik", u"isch") and
                      u"e" not in r2[-len(suffix)-1:-len(suffix)]):
                    word = word[:-len(suffix)]

                elif suffix in (u"lich", u"heit"):
                    if (u"er" in r1[-len(suffix)-2:-len(suffix)] or
                        u"en" in r1[-len(suffix)-2:-len(suffix)]):
                        word = word[:-len(suffix)-2]
                    else:
                        word = word[:-len(suffix)]

                elif suffix == u"keit":
                    if u"lich" in r2[-len(suffix)-4:-len(suffix)]:
                        word = word[:-len(suffix)-4]

                    elif u"ig" in r2[-len(suffix)-2:-len(suffix)]:
                        word = word[:-len(suffix)-2]
                    else:
                        word = word[:-len(suffix)]
                break

        # Umlaut accents are removed and
        # 'u' and 'y' are put back into lower case.
        word = (word.replace(u"\xE4", u"a").replace(u"\xF6", u"o")
                    .replace(u"\xFC", u"u").replace(u"U", u"u")
                    .replace(u"Y", u"y"))


        return word


class HungarianStemmer(SnowballStemmer):
    """The Hungarian Snowball stemmer.

    @cvar __vowels: The Hungarian vowels.
    @type __vowels: C{unicode}
    @cvar __digraphs: The Hungarian digraphs.
    @type __digraphs: C{tuple}
    @cvar __double_consonants: The Hungarian double consonants.
    @type __double_consonants: C{tuple}
    @cvar __step1_suffixes: Suffixes to be deleted in step 1 of the algorithm.
    @type __step1_suffixes: C{tuple}
    @cvar __step2_suffixes: Suffixes to be deleted in step 2 of the algorithm.
    @type __step2_suffixes: C{tuple}
    @cvar __step3_suffixes: Suffixes to be deleted in step 3 of the algorithm.
    @type __step3_suffixes: C{tuple}
    @cvar __step4_suffixes: Suffixes to be deleted in step 4 of the algorithm.
    @type __step4_suffixes: C{tuple}
    @cvar __step5_suffixes: Suffixes to be deleted in step 5 of the algorithm.
    @type __step5_suffixes: C{tuple}
    @cvar __step6_suffixes: Suffixes to be deleted in step 6 of the algorithm.
    @type __step6_suffixes: C{tuple}
    @cvar __step7_suffixes: Suffixes to be deleted in step 7 of the algorithm.
    @type __step7_suffixes: C{tuple}
    @cvar __step8_suffixes: Suffixes to be deleted in step 8 of the algorithm.
    @type __step8_suffixes: C{tuple}
    @cvar __step9_suffixes: Suffixes to be deleted in step 9 of the algorithm.
    @type __step9_suffixes: C{tuple}
    @note: A detailed description of the Hungarian
           stemming algorithm can be found under
           U{http://snowball.tartarus.org/algorithms
           /hungarian/stemmer.html}.

    """

    zope.interface.implements(interfaces.IHungarianStemmer)

    __vowels = u"aeiou\xF6\xFC\xE1\xE9\xED\xF3\xF5\xFA\xFB"
    __digraphs = (u"cs", u"dz", u"dzs", u"gy", u"ly", u"ny", u"ty", u"zs")
    __double_consonants = (u"bb", u"cc", u"ccs", u"dd", u"ff", u"gg", 
                             u"ggy", u"jj", u"kk", u"ll", u"lly", u"mm", 
                             u"nn", u"nny", u"pp", u"rr", u"ss", u"ssz", 
                             u"tt", u"tty", u"vv", u"zz", u"zzs")

    __step1_suffixes = (u"al", u"el")
    __step2_suffixes = (u'k\xE9ppen', u'onk\xE9nt', u'enk\xE9nt',
                        u'ank\xE9nt', u'k\xE9pp', u'k\xE9nt', u'ban',
                        u'ben', u'nak', u'nek', u'val', u'vel', u't\xF3l',
                        u't\xF5l', u'r\xF3l', u'r\xF5l', u'b\xF3l',
                        u'b\xF5l', u'hoz', u'hez', u'h\xF6z', 
                        u'n\xE1l', u'n\xE9l', u'\xE9rt', u'kor', 
                        u'ba', u'be', u'ra', u're', u'ig', u'at', u'et', 
                        u'ot', u'\xF6t', u'ul', u'\xFCl', u'v\xE1', 
                        u'v\xE9', u'en', u'on', u'an', u'\xF6n', 
                        u'n', u't')
    __step3_suffixes = (u"\xE1nk\xE9nt", u"\xE1n", u"\xE9n")
    __step4_suffixes = (u'astul', u'est\xFCl', u'\xE1stul',
                        u'\xE9st\xFCl', u'stul', u'st\xFCl')
    __step5_suffixes = (u"\xE1", u"\xE9")
    __step6_suffixes = (u'ok\xE9', u'\xF6k\xE9', u'ak\xE9',
                        u'ek\xE9', u'\xE1k\xE9', u'\xE1\xE9i',
                        u'\xE9k\xE9', u'\xE9\xE9i', u'k\xE9',
                        u'\xE9i', u'\xE9\xE9', u'\xE9')
    __step7_suffixes = (u'\xE1juk', u'\xE9j\xFCk', u'\xFCnk', 
                        u'unk', u'juk', u'j\xFCk', u'\xE1nk', 
                        u'\xE9nk', u'nk', u'uk', u'\xFCk', u'em', 
                        u'om', u'am', u'od', u'ed', u'ad', u'\xF6d', 
                        u'ja', u'je', u'\xE1m', u'\xE1d', u'\xE9m', 
                        u'\xE9d', u'm', u'd', u'a', u'e', u'o', 
                        u'\xE1', u'\xE9')
    __step8_suffixes = (u'jaitok', u'jeitek', u'jaink', u'jeink', u'aitok',
                        u'eitek', u'\xE1itok', u'\xE9itek', u'jaim',
                        u'jeim', u'jaid', u'jeid', u'eink', u'aink', 
                        u'itek', u'jeik', u'jaik', u'\xE1ink', 
                        u'\xE9ink', u'aim', u'eim', u'aid', u'eid', 
                        u'jai', u'jei', u'ink', u'aik', u'eik', 
                        u'\xE1im', u'\xE1id', u'\xE1ik', u'\xE9im', 
                        u'\xE9id', u'\xE9ik', u'im', u'id', u'ai', 
                        u'ei', u'ik', u'\xE1i', u'\xE9i', u'i')
    __step9_suffixes = (u"\xE1k", u"\xE9k", u"\xF6k", u"ok",
                        u"ek", u"ak", u"k")

    def stem(self, word):
        """
        Stem an Hungarian word and return the stemmed form.

        @param word: The word that is stemmed.
        @type word: C{str, unicode}
        @return: The stemmed form.
        @rtype: C{unicode}

        """
        # lower, since all the rules are lower-cased
        word = word.lower()
        # don't stem stopwords
        if word in self.stopwords:
            return word

        r1 = self.__r1_hungarian(word, self.__vowels, self.__digraphs)

        # STEP 1: Remove instrumental case
        if r1.endswith(self.__step1_suffixes):
            for double_cons in self.__double_consonants:
                if word[-2-len(double_cons):-2] == double_cons:
                    word = u"".join((word[:-4], word[-3]))

                    if r1[-2-len(double_cons):-2] == double_cons:
                        r1 = u"".join((r1[:-4], r1[-3]))
                    break

        # STEP 2: Remove frequent cases
        for suffix in self.__step2_suffixes:
            if word.endswith(suffix):
                if r1.endswith(suffix):
                    word = word[:-len(suffix)]
                    r1 = r1[:-len(suffix)]

                    if r1.endswith(u"\xE1"):
                        word = u"".join((word[:-1], u"a"))
                        r1 = u"".join((r1[:-1], u"a"))

                    elif r1.endswith(u"\xE9"):
                        word = u"".join((word[:-1], u"e"))
                        r1 = u"".join((r1[:-1], u"e"))
                break

        # STEP 3: Remove special cases
        for suffix in self.__step3_suffixes:
            if r1.endswith(suffix):
                if suffix == u"\xE9n":
                    word = u"".join((word[:-2], u"e"))
                    r1 = u"".join((r1[:-2], u"e"))
                else:
                    word = u"".join((word[:-len(suffix)], u"a"))
                    r1 = u"".join((r1[:-len(suffix)], u"a"))
                break

        # STEP 4: Remove other cases
        for suffix in self.__step4_suffixes:
            if r1.endswith(suffix):
                if suffix == u"\xE1stul":
                    word = u"".join((word[:-5], u"a"))
                    r1 = u"".join((r1[:-5], u"a"))

                elif suffix == u"\xE9st\xFCl":
                    word = u"".join((word[:-5], u"e"))
                    r1 = u"".join((r1[:-5], u"e"))
                else:
                    word = word[:-len(suffix)]
                    r1 = r1[:-len(suffix)]
                break

        # STEP 5: Remove factive case
        for suffix in self.__step5_suffixes:
            if r1.endswith(suffix):
                for double_cons in self.__double_consonants:
                    if word[-1-len(double_cons):-1] == double_cons:
                        word = u"".join((word[:-3], word[-2]))

                        if r1[-1-len(double_cons):-1] == double_cons:
                            r1 = u"".join((r1[:-3], r1[-2]))
                        break

        # STEP 6: Remove owned
        for suffix in self.__step6_suffixes:
            if r1.endswith(suffix):
                if suffix in (u"\xE1k\xE9", u"\xE1\xE9i"):
                    word = u"".join((word[:-3], u"a"))
                    r1 = u"".join((r1[:-3], u"a"))

                elif suffix in (u"\xE9k\xE9", u"\xE9\xE9i",
                                u"\xE9\xE9"):
                    word = u"".join((word[:-len(suffix)], u"e"))
                    r1 = u"".join((r1[:-len(suffix)], u"e"))
                else:
                    word = word[:-len(suffix)]
                    r1 = r1[:-len(suffix)]
                break

        # STEP 7: Remove singular owner suffixes
        for suffix in self.__step7_suffixes:
            if word.endswith(suffix):
                if r1.endswith(suffix):
                    if suffix in (u"\xE1nk", u"\xE1juk", u"\xE1m",
                                  u"\xE1d", u"\xE1"):
                        word = u"".join((word[:-len(suffix)], u"a"))
                        r1 = u"".join((r1[:-len(suffix)], u"a"))

                    elif suffix in (u"\xE9nk", u"\xE9j\xFCk",
                                    u"\xE9m", u"\xE9d", u"\xE9"):
                        word = u"".join((word[:-len(suffix)], u"e"))
                        r1 = u"".join((r1[:-len(suffix)], u"e"))
                    else:
                        word = word[:-len(suffix)]
                        r1 = r1[:-len(suffix)]
                break

        # STEP 8: Remove plural owner suffixes
        for suffix in self.__step8_suffixes:
            if word.endswith(suffix):
                if r1.endswith(suffix):
                    if suffix in (u"\xE1im", u"\xE1id", u"\xE1i",
                                  u"\xE1ink", u"\xE1itok", u"\xE1ik"):
                        word = u"".join((word[:-len(suffix)], u"a"))
                        r1 = u"".join((r1[:-len(suffix)], u"a"))

                    elif suffix in (u"\xE9im", u"\xE9id", u"\xE9i",
                                    u"\xE9ink", u"\xE9itek", u"\xE9ik"):
                        word = u"".join((word[:-len(suffix)], u"e"))
                        r1 = u"".join((r1[:-len(suffix)], u"e"))
                    else:
                        word = word[:-len(suffix)]
                        r1 = r1[:-len(suffix)]
                break

        # STEP 9: Remove plural suffixes
        for suffix in self.__step9_suffixes:
            if word.endswith(suffix):
                if r1.endswith(suffix):
                    if suffix == u"\xE1k":
                        word = u"".join((word[:-2], u"a"))
                    elif suffix == u"\xE9k":
                        word = u"".join((word[:-2], u"e"))
                    else:
                        word = word[:-len(suffix)]
                break


        return word

    def __r1_hungarian(self, word, vowels, digraphs):
        """
        Return the region R1 that is used by the Hungarian stemmer.

        If the word begins with a vowel, R1 is defined as the region
        after the first consonant or digraph (= two letters stand for
        one phoneme) in the word. If the word begins with a consonant,
        it is defined as the region after the first vowel in the word.
        If the word does not contain both a vowel and consonant, R1
        is the null region at the end of the word.

        @param word: The Hungarian word whose region R1 is determined.
        @type word: C{str, unicode}
        @param vowels: The Hungarian vowels that are used to determine
                       the region R1.
        @type vowels: C{unicode}
        @param digraphs: The digraphs that are used to determine the
                         region R1.
        @type digraphs: C{tuple}
        @return: C{r1}, the region R1 for the respective word.
        @rtype: C{unicode}
        @note: This helper method is invoked by the stem method of the subclass
               L{HungarianStemmer}. It is not to be invoked directly!

        """
        r1 = u""
        if word[0] in vowels:
            for digraph in digraphs:
                if digraph in word[1:]:
                    r1 = word[word.index(digraph[-1])+1:]
                    return r1

            for i in xrange(1, len(word)):
                if word[i] not in vowels:
                    r1 = word[i+1:]
                    break
        else:
            for i in xrange(1, len(word)):
                if word[i] in vowels:
                    r1 = word[i+1:]
                    break

        return r1


class ItalianStemmer(_StandardStemmer):
    """The Italian Snowball stemmer.

    @cvar __vowels: The Italian vowels.
    @type __vowels: C{unicode}
    @cvar __step0_suffixes: Suffixes to be deleted in step 0 of the algorithm.
    @type __step0_suffixes: C{tuple}
    @cvar __step1_suffixes: Suffixes to be deleted in step 1 of the algorithm.
    @type __step1_suffixes: C{tuple}
    @cvar __step2_suffixes: Suffixes to be deleted in step 2 of the algorithm.
    @type __step2_suffixes: C{tuple}
    @note: A detailed description of the Italian
           stemming algorithm can be found under
           U{http://snowball.tartarus.org/algorithms
           /italian/stemmer.html}.

    """

    zope.interface.implements(interfaces.IItalianStemmer)

    __vowels = u"aeiou\xE0\xE8\xEC\xF2\xF9"
    __step0_suffixes = (u'gliela', u'gliele', u'glieli', u'glielo', 
                        u'gliene', u'sene', u'mela', u'mele', u'meli', 
                        u'melo', u'mene', u'tela', u'tele', u'teli', 
                        u'telo', u'tene', u'cela', u'cele', u'celi', 
                        u'celo', u'cene', u'vela', u'vele', u'veli', 
                        u'velo', u'vene', u'gli', u'ci', u'la', u'le',
                        u'li', u'lo', u'mi', u'ne', u'si', u'ti', u'vi')
    __step1_suffixes = (u'atrice', u'atrici', u'azione', u'azioni', 
                        u'uzione', u'uzioni', u'usione', u'usioni', 
                        u'amento', u'amenti', u'imento', u'imenti', 
                        u'amente', u'abile', u'abili', u'ibile', u'ibili', 
                        u'mente', u'atore', u'atori', u'logia', u'logie', 
                        u'anza', u'anze', u'iche', u'ichi', u'ismo', 
                        u'ismi', u'ista', u'iste', u'isti', u'ist\xE0', 
                        u'ist\xE8', u'ist\xEC', u'ante', u'anti', 
                        u'enza', u'enze', u'ico', u'ici', u'ica', u'ice', 
                        u'oso', u'osi', u'osa', u'ose', u'it\xE0',
                        u'ivo', u'ivi', u'iva', u'ive')
    __step2_suffixes = (u'erebbero', u'irebbero', u'assero', u'assimo',
                        u'eranno', u'erebbe', u'eremmo', u'ereste',
                        u'eresti', u'essero', u'iranno', u'irebbe', 
                        u'iremmo', u'ireste', u'iresti', u'iscano', 
                        u'iscono', u'issero', u'arono', u'avamo', u'avano', 
                        u'avate', u'eremo', u'erete', u'erono', u'evamo', 
                        u'evano', u'evate', u'iremo', u'irete', u'irono', 
                        u'ivamo', u'ivano', u'ivate', u'ammo', u'ando', 
                        u'asse', u'assi', u'emmo', u'enda', u'ende', 
                        u'endi', u'endo', u'erai', u'erei', u'Yamo', 
                        u'iamo', u'immo', u'irai', u'irei', u'isca', 
                        u'isce', u'isci', u'isco', u'ano', u'are', u'ata',
                        u'ate', u'ati', u'ato', u'ava', u'avi', u'avo',
                        u'er\xE0', u'ere', u'er\xF2', u'ete', u'eva',
                        u'evi', u'evo', u'ir\xE0', u'ire', u'ir\xF2',
                        u'ita', u'ite', u'iti', u'ito', u'iva', u'ivi', 
                        u'ivo', u'ono', u'uta', u'ute', u'uti', u'uto', 
                        u'ar', u'ir')

    def stem(self, word):
        """
        Stem an Italian word and return the stemmed form.
        @param word: The word that is stemmed.
        @type word: C{str, unicode}
        @return: The stemmed form.
        @rtype: C{unicode}

        """
        # lower, since all the rules are lower-cased
        word = word.lower()
        # don't stem stopwords
        if word in self.stopwords:
            return word

        step1_success = False

        # All acute accents are replaced by grave accents.
        word = (word.replace(u"\xE1", u"\xE0")
                    .replace(u"\xE9", u"\xE8")
                    .replace(u"\xED", u"\xEC")
                    .replace(u"\xF3", u"\xF2")
                    .replace(u"\xFA", u"\xF9"))

        # Every occurrence of 'u' after 'q'
        # is put into upper case.
        for i in xrange(1, len(word)):
            if word[i-1] == u"q" and word[i] == u"u":
                word = u"".join((word[:i], u"U", word[i+1:]))

        # Every occurrence of 'u' and 'i'
        # between vowels is put into upper case.
        for i in xrange(1, len(word)-1):
            if word[i-1] in self.__vowels and word[i+1] in self.__vowels:
                if word[i] == u"u":
                    word = u"".join((word[:i], u"U", word[i+1:]))

                elif word [i] == u"i":
                    word = u"".join((word[:i], u"I", word[i+1:]))

        r1, r2 = self._r1r2_standard(word, self.__vowels)
        rv = self._rv_standard(word, self.__vowels)

        # STEP 0: Attached pronoun
        for suffix in self.__step0_suffixes:
            if rv.endswith(suffix):
                if rv[-len(suffix)-4:-len(suffix)] in (u"ando", u"endo"):
                    word = word[:-len(suffix)]
                    r1 = r1[:-len(suffix)]
                    r2 = r2[:-len(suffix)]
                    rv = rv[:-len(suffix)]

                elif (rv[-len(suffix)-2:-len(suffix)] in
                      (u"ar", u"er", u"ir")):
                    word = u"".join((word[:-len(suffix)], u"e"))
                    r1 = u"".join((r1[:-len(suffix)], u"e"))
                    r2 = u"".join((r2[:-len(suffix)], u"e"))
                    rv = u"".join((rv[:-len(suffix)], u"e"))
                break

        # STEP 1: Standard suffix removal
        for suffix in self.__step1_suffixes:
            if word.endswith(suffix):
                if suffix == u"amente" and r1.endswith(suffix):
                    step1_success = True
                    word = word[:-6]
                    r2 = r2[:-6]
                    rv = rv[:-6]

                    if r2.endswith(u"iv"):
                        word = word[:-2]
                        r2 = r2[:-2]
                        rv = rv[:-2]

                        if r2.endswith(u"at"):
                            word = word[:-2]
                            rv = rv[:-2]

                    elif r2.endswith((u"os", u"ic")):
                        word = word[:-2]
                        rv = rv[:-2]

                    elif r2 .endswith(u"abil"):
                        word = word[:-4]
                        rv = rv[:-4]

                elif (suffix in (u"amento", u"amenti", 
                                 u"imento", u"imenti") and
                      rv.endswith(suffix)):
                    step1_success = True
                    word = word[:-6]
                    rv = rv[:-6]

                elif r2.endswith(suffix):
                    step1_success = True
                    if suffix in (u"azione", u"azioni", u"atore", u"atori"):
                        word = word[:-len(suffix)]
                        r2 = r2[:-len(suffix)]
                        rv = rv[:-len(suffix)]

                        if r2.endswith(u"ic"):
                            word = word[:-2]
                            rv = rv[:-2]

                    elif suffix in (u"logia", u"logie"):
                        word = word[:-2]
                        rv = word[:-2]

                    elif suffix in (u"uzione", u"uzioni", 
                                    u"usione", u"usioni"):
                        word = word[:-5]
                        rv = rv[:-5]

                    elif suffix in (u"enza", u"enze"):
                        word = u"".join((word[:-2], u"te"))
                        rv = u"".join((rv[:-2], u"te"))

                    elif suffix == u"it\xE0":
                        word = word[:-3]
                        r2 = r2[:-3]
                        rv = rv[:-3]

                        if r2.endswith((u"ic", u"iv")):
                            word = word[:-2]
                            rv = rv[:-2]

                        elif r2.endswith(u"abil"):
                            word = word[:-4]
                            rv = rv[:-4]

                    elif suffix in (u"ivo", u"ivi", u"iva", u"ive"):
                        word = word[:-3]
                        r2 = r2[:-3]
                        rv = rv[:-3]

                        if r2.endswith(u"at"):
                            word = word[:-2]
                            r2 = r2[:-2]
                            rv = rv[:-2]

                            if r2.endswith(u"ic"):
                                word = word[:-2]
                                rv = rv[:-2]
                    else:
                        word = word[:-len(suffix)]
                        rv = rv[:-len(suffix)]
                break

        # STEP 2: Verb suffixes
        if not step1_success:
            for suffix in self.__step2_suffixes:
                if rv.endswith(suffix):
                    word = word[:-len(suffix)]
                    rv = rv[:-len(suffix)]
                    break

        # STEP 3a
        if rv.endswith((u"a", u"e", u"i", u"o", u"\xE0", u"\xE8",
                        u"\xEC", u"\xF2")):
            word = word[:-1]
            rv = rv[:-1]

            if rv.endswith(u"i"):
                word = word[:-1]
                rv = rv[:-1]

        # STEP 3b
        if rv.endswith((u"ch", u"gh")):
            word = word[:-1]

        word = word.replace(u"I", u"i").replace(u"U", u"u")


        return word


class NorwegianStemmer(_ScandinavianStemmer):
    """The Norwegian Snowball stemmer.

    @cvar __vowels: The Norwegian vowels.
    @type __vowels: C{unicode}
    @cvar __s_ending: Letters that may directly appear before a word final 's'.
    @type __s_ending: C{unicode}
    @cvar __step1_suffixes: Suffixes to be deleted in step 1 of the algorithm.
    @type __step1_suffixes: C{tuple}
    @cvar __step2_suffixes: Suffixes to be deleted in step 2 of the algorithm.
    @type __step2_suffixes: C{tuple}
    @cvar __step3_suffixes: Suffixes to be deleted in step 3 of the algorithm.
    @type __step3_suffixes: C{tuple}
    @note: A detailed description of the Norwegian
           stemming algorithm can be found under
           U{http://snowball.tartarus.org/algorithms
           /norwegian/stemmer.html}.

    """

    zope.interface.implements(interfaces.INorwegianStemmer)

    __vowels = u"aeiouy\xE6\xE5\xF8"
    __s_ending = u"bcdfghjlmnoprtvyz"
    __step1_suffixes = (u"hetenes", u"hetene", u"hetens", u"heter", 
                        u"heten", u"endes", u"ande", u"ende", u"edes", 
                        u"enes", u"erte", u"ede", u"ane", u"ene", u"ens", 
                        u"ers", u"ets", u"het", u"ast", u"ert", u"en", 
                        u"ar", u"er", u"as", u"es", u"et", u"a", u"e", u"s")

    __step2_suffixes = (u"dt", u"vt")

    __step3_suffixes = (u"hetslov", u"eleg", u"elig", u"elov", u"slov", 
                          u"leg", u"eig", u"lig", u"els", u"lov", u"ig")

    def stem(self, word):
        """
        Stem a Norwegian word and return the stemmed form.
        @param word: The word that is stemmed.
        @type word: C{str, unicode}
        @return: The stemmed form.
        @rtype: C{unicode}

        """
        # lower, since all the rules are lower-cased
        word = word.lower()
        # don't stem stopwords
        if word in self.stopwords:
            return word

        r1 = self._r1_scandinavian(word, self.__vowels)

        # STEP 1
        for suffix in self.__step1_suffixes:
            if r1.endswith(suffix):
                if suffix in (u"erte", u"ert"):
                    word = u"".join((word[:-len(suffix)], u"er"))
                    r1 = u"".join((r1[:-len(suffix)], u"er"))

                elif suffix == u"s":
                    if (word[-2] in self.__s_ending or
                        (word[-2] == u"k" and word[-3] not in self.__vowels)):
                        word = word[:-1]
                        r1 = r1[:-1]
                else:
                    word = word[:-len(suffix)]
                    r1 = r1[:-len(suffix)]
                break

        # STEP 2
        for suffix in self.__step2_suffixes:
            if r1.endswith(suffix):
                word = word[:-1]
                r1 = r1[:-1]
                break

        # STEP 3
        for suffix in self.__step3_suffixes:
            if r1.endswith(suffix):
                word = word[:-len(suffix)]
                break


        return word


class PortugueseStemmer(_StandardStemmer):
    """The Portuguese Snowball stemmer.

    @cvar __vowels: The Portuguese vowels.
    @type __vowels: C{unicode}
    @cvar __step1_suffixes: Suffixes to be deleted in step 1 of the algorithm.
    @type __step1_suffixes: C{tuple}
    @cvar __step2_suffixes: Suffixes to be deleted in step 2 of the algorithm.
    @type __step2_suffixes: C{tuple}
    @cvar __step4_suffixes: Suffixes to be deleted in step 4 of the algorithm.
    @type __step4_suffixes: C{tuple}
    @note: A detailed description of the Portuguese
           stemming algorithm can be found under
           U{http://snowball.tartarus.org/algorithms
           /portuguese/stemmer.html}.

    """

    zope.interface.implements(interfaces.IPortugueseStemmer)

    __vowels = u"aeiou\xE1\xE9\xED\xF3\xFA\xE2\xEA\xF4"
    __step1_suffixes = (u'amentos', u'imentos', u'uciones', u'amento',
                        u'imento', u'adoras', u'adores', u'a\xE7o~es',
                        u'log\xEDas', u'\xEAncias', u'amente', 
                        u'idades', u'ismos', u'istas', u'adora', 
                        u'a\xE7a~o', u'antes', u'\xE2ncia', 
                        u'log\xEDa', u'uci\xF3n', u'\xEAncia', 
                        u'mente', u'idade', u'ezas', u'icos', u'icas', 
                        u'ismo', u'\xE1vel', u'\xEDvel', u'ista', 
                        u'osos', u'osas', u'ador', u'ante', u'ivas', 
                        u'ivos', u'iras', u'eza', u'ico', u'ica', 
                        u'oso', u'osa', u'iva', u'ivo', u'ira')
    __step2_suffixes = (u'ar\xEDamos', u'er\xEDamos', u'ir\xEDamos',
                        u'\xE1ssemos', u'\xEAssemos', u'\xEDssemos',
                        u'ar\xEDeis', u'er\xEDeis', u'ir\xEDeis',
                        u'\xE1sseis', u'\xE9sseis', u'\xEDsseis',
                        u'\xE1ramos', u'\xE9ramos', u'\xEDramos',
                        u'\xE1vamos', u'aremos', u'eremos', u'iremos',
                        u'ariam', u'eriam', u'iriam', u'assem', u'essem',
                        u'issem', u'ara~o', u'era~o', u'ira~o', u'arias',
                        u'erias', u'irias', u'ardes', u'erdes', u'irdes',
                        u'asses', u'esses', u'isses', u'astes', u'estes',
                        u'istes', u'\xE1reis', u'areis', u'\xE9reis',
                        u'ereis', u'\xEDreis', u'ireis', u'\xE1veis',
                        u'\xEDamos', u'armos', u'ermos', u'irmos', 
                        u'aria', u'eria', u'iria', u'asse', u'esse', 
                        u'isse', u'aste', u'este', u'iste', u'arei', 
                        u'erei', u'irei', u'aram', u'eram', u'iram', 
                        u'avam', u'arem', u'erem', u'irem',
                        u'ando', u'endo', u'indo', u'adas', u'idas',
                        u'ar\xE1s', u'aras', u'er\xE1s', u'eras',
                        u'ir\xE1s', u'avas', u'ares', u'eres', u'ires',
                        u'\xEDeis', u'ados', u'idos', u'\xE1mos', 
                        u'amos', u'emos', u'imos', u'iras', u'ada', u'ida', 
                        u'ar\xE1', u'ara', u'er\xE1', u'era', 
                        u'ir\xE1', u'ava', u'iam', u'ado', u'ido', 
                        u'ias', u'ais', u'eis', u'ira', u'ia', u'ei', u'am', 
                        u'em', u'ar', u'er', u'ir', u'as',
                        u'es', u'is', u'eu', u'iu', u'ou')
    __step4_suffixes = (u"os", u"a", u"i", u"o", u"\xE1", 
                        u"\xED", u"\xF3")

    def stem(self, word):
        """
        Stem a Portuguese word and return the stemmed form.
        @param word: The word that is stemmed.
        @type word: C{str, unicode}
        @return: The stemmed form.
        @rtype: C{unicode}

        """
        # lower, since all the rules are lower-cased
        word = word.lower()
        # don't stem stopwords
        if word in self.stopwords:
            return word

        step1_success = False
        step2_success = False

        word = (word.lower()
                    .replace(u"\xE3", u"a~")
                    .replace(u"\xF5", u"o~"))

        r1, r2 = self._r1r2_standard(word, self.__vowels)
        rv = self._rv_standard(word, self.__vowels)

        # STEP 1: Standard suffix removal
        for suffix in self.__step1_suffixes:
            if word.endswith(suffix):
                if suffix == u"amente" and r1.endswith(suffix):
                    step1_success = True

                    word = word[:-6]
                    r2 = r2[:-6]
                    rv = rv[:-6]

                    if r2.endswith(u"iv"):
                        word = word[:-2]
                        r2 = r2[:-2]
                        rv = rv[:-2]

                        if r2.endswith(u"at"):
                            word = word[:-2]
                            rv = rv[:-2]

                    elif r2.endswith((u"os", u"ic", u"ad")):
                        word = word[:-2]
                        rv = rv[:-2]

                elif (suffix in (u"ira", u"iras") and rv.endswith(suffix) and
                      word[-len(suffix)-1:-len(suffix)] == u"e"):
                    step1_success = True

                    word = u"".join((word[:-len(suffix)], u"ir"))
                    rv = u"".join((rv[:-len(suffix)], u"ir"))

                elif r2.endswith(suffix):
                    step1_success = True

                    if suffix in (u"log\xEDa", u"log\xEDas"):
                        word = word[:-2]
                        rv = rv[:-2]

                    elif suffix in (u"uci\xF3n", u"uciones"):
                        word = u"".join((word[:-len(suffix)], u"u"))
                        rv = u"".join((rv[:-len(suffix)], u"u"))

                    elif suffix in (u"\xEAncia", u"\xEAncias"):
                        word = u"".join((word[:-len(suffix)], u"ente"))
                        rv = u"".join((rv[:-len(suffix)], u"ente"))

                    elif suffix == u"mente":
                        word = word[:-5]
                        r2 = r2[:-5]
                        rv = rv[:-5]

                        if r2.endswith((u"ante", u"avel", u"\xEDvel")):
                            word = word[:-4]
                            rv = rv[:-4]

                    elif suffix in (u"idade", u"idades"):
                        word = word[:-len(suffix)]
                        r2 = r2[:-len(suffix)]
                        rv = rv[:-len(suffix)]

                        if r2.endswith((u"ic", u"iv")):
                            word = word[:-2]
                            rv = rv[:-2]

                        elif r2.endswith(u"abil"):
                            word = word[:-4]
                            rv = rv[:-4]

                    elif suffix in (u"iva", u"ivo", u"ivas", u"ivos"):
                        word = word[:-len(suffix)]
                        r2 = r2[:-len(suffix)]
                        rv = rv[:-len(suffix)]

                        if r2.endswith(u"at"):
                            word = word[:-2]
                            rv = rv[:-2]
                    else:
                        word = word[:-len(suffix)]
                        rv = rv[:-len(suffix)]
                break

        # STEP 2: Verb suffixes
        if not step1_success:
            for suffix in self.__step2_suffixes:
                if rv.endswith(suffix):
                    step2_success = True

                    word = word[:-len(suffix)]
                    rv = rv[:-len(suffix)]
                    break

        # STEP 3
        if step1_success or step2_success:
            if rv.endswith(u"i") and word[-2] == u"c":
                word = word[:-1]
                rv = rv[:-1]

        ### STEP 4: Residual suffix
        if not step1_success and not step2_success:
            for suffix in self.__step4_suffixes:
                if rv.endswith(suffix):
                    word = word[:-len(suffix)]
                    rv = rv[:-len(suffix)]
                    break

        # STEP 5
        if rv.endswith((u"e", u"\xE9", u"\xEA")):
            word = word[:-1]
            rv = rv[:-1]

            if ((word.endswith(u"gu") and rv.endswith(u"u")) or
                (word.endswith(u"ci") and rv.endswith(u"i"))):
                word = word[:-1]

        elif word.endswith(u"\xE7"):
            word = u"".join((word[:-1], u"c"))

        word = word.replace(u"a~", u"\xE3").replace(u"o~", u"\xF5")


        return word


class RomanianStemmer(_StandardStemmer):
    """The Romanian Snowball stemmer.

    @cvar __vowels: The Romanian vowels.
    @type __vowels: C{unicode}
    @cvar __step0_suffixes: Suffixes to be deleted in step 0 of the algorithm.
    @type __step0_suffixes: C{tuple}
    @cvar __step1_suffixes: Suffixes to be deleted in step 1 of the algorithm.
    @type __step1_suffixes: C{tuple}
    @cvar __step2_suffixes: Suffixes to be deleted in step 2 of the algorithm.
    @type __step2_suffixes: C{tuple}
    @cvar __step3_suffixes: Suffixes to be deleted in step 3 of the algorithm.
    @type __step3_suffixes: C{tuple}
    @note: A detailed description of the Romanian
           stemming algorithm can be found under
           U{http://snowball.tartarus.org/algorithms
           /romanian/stemmer.html}.

    """

    zope.interface.implements(interfaces.IRomanianStemmer)

    __vowels = u"aeiou\u0103\xE2\xEE"
    __step0_suffixes = (u'iilor', u'ului', u'elor', u'iile', u'ilor', 
                        u'atei', u'a\u0163ie', u'a\u0163ia', u'aua', 
                        u'ele', u'iua', u'iei', u'ile', u'ul', u'ea', 
                        u'ii')
    __step1_suffixes = (u'abilitate', u'abilitati', u'abilit\u0103\u0163i',
                        u'ibilitate', u'abilit\u0103i', u'ivitate', 
                        u'ivitati', u'ivit\u0103\u0163i', u'icitate', 
                        u'icitati', u'icit\u0103\u0163i', u'icatori', 
                        u'ivit\u0103i', u'icit\u0103i', u'icator', 
                        u'a\u0163iune', u'atoare', u'\u0103toare', 
                        u'i\u0163iune', u'itoare', u'iciva', u'icive', 
                        u'icivi', u'iciv\u0103', u'icala', u'icale', 
                        u'icali', u'ical\u0103', u'ativa', u'ative', 
                        u'ativi', u'ativ\u0103', u'atori', u'\u0103tori', 
                        u'itiva', u'itive', u'itivi', u'itiv\u0103', 
                        u'itori', u'iciv', u'ical', u'ativ', u'ator', 
                        u'\u0103tor', u'itiv', u'itor')
    __step2_suffixes = (u'abila', u'abile', u'abili', u'abil\u0103', 
                        u'ibila', u'ibile', u'ibili', u'ibil\u0103', 
                        u'atori', u'itate', u'itati', u'it\u0103\u0163i', 
                        u'abil', u'ibil', u'oasa', u'oas\u0103', u'oase', 
                        u'anta', u'ante', u'anti', u'ant\u0103', u'ator', 
                        u'it\u0103i', u'iune', u'iuni', u'isme', u'ista', 
                        u'iste', u'isti', u'ist\u0103', u'i\u015Fti', 
                        u'ata', u'at\u0103', u'ati', u'ate', u'uta',
                        u'ut\u0103', u'uti', u'ute', u'ita', u'it\u0103', 
                        u'iti', u'ite', u'ica', u'ice', u'ici', u'ic\u0103', 
                        u'osi', u'o\u015Fi', u'ant', u'iva', u'ive', u'ivi', 
                        u'iv\u0103', u'ism', u'ist', u'at', u'ut', u'it', 
                        u'ic', u'os', u'iv')
    __step3_suffixes = (u'seser\u0103\u0163i', u'aser\u0103\u0163i',
                        u'iser\u0103\u0163i', u'\xE2ser\u0103\u0163i',
                        u'user\u0103\u0163i', u'seser\u0103m', 
                        u'aser\u0103m', u'iser\u0103m', u'\xE2ser\u0103m', 
                        u'user\u0103m', u'ser\u0103\u0163i', u'sese\u015Fi', 
                        u'seser\u0103', u'easc\u0103', u'ar\u0103\u0163i', 
                        u'ur\u0103\u0163i', u'ir\u0103\u0163i', 
                        u'\xE2r\u0103\u0163i', u'ase\u015Fi', 
                        u'aser\u0103', u'ise\u015Fi', u'iser\u0103', 
                        u'\xe2se\u015Fi', u'\xE2ser\u0103',
                        u'use\u015Fi', u'user\u0103', u'ser\u0103m', 
                        u'sesem', u'indu', u'\xE2ndu', u'eaz\u0103', 
                        u'e\u015Fti', u'e\u015Fte', u'\u0103\u015Fti', 
                        u'\u0103\u015Fte', u'ea\u0163i', u'ia\u0163i', 
                        u'ar\u0103m', u'ur\u0103m', u'ir\u0103m', 
                        u'\xE2r\u0103m', u'asem', u'isem',
                        u'\xE2sem', u'usem', u'se\u015Fi', u'ser\u0103',
                        u'sese', u'are', u'ere', u'ire', u'\xE2re', 
                        u'ind', u'\xE2nd', u'eze', u'ezi', u'esc', 
                        u'\u0103sc', u'eam', u'eai', u'eau', u'iam', 
                        u'iai', u'iau', u'a\u015Fi', u'ar\u0103', 
                        u'u\u015Fi', u'ur\u0103', u'i\u015Fi', u'ir\u0103', 
                        u'\xE2\u015Fi', u'\xe2r\u0103', u'ase',
                        u'ise', u'\xE2se', u'use', u'a\u0163i', 
                        u'e\u0163i', u'i\u0163i', u'\xe2\u0163i', u'sei', 
                        u'ez', u'am', u'ai', u'au', u'ea', u'ia', u'ui', 
                        u'\xE2i', u'\u0103m', u'em', u'im', u'\xE2m', 
                        u'se')

    def stem(self, word):
        """
        Stem a Romanian word and return the stemmed form.
        @param word: The word that is stemmed.
        @type word: C{str, unicode}
        @return: The stemmed form.
        @rtype: C{unicode}

        """
        # lower, since all the rules are lower-cased
        word = word.lower()
        # don't stem stopwords
        if word in self.stopwords:
            return word

        step1_success = False
        step2_success = False

        for i in xrange(1, len(word)-1):
            if word[i-1] in self.__vowels and word[i+1] in self.__vowels:
                if word[i] == u"u":
                    word = u"".join((word[:i], u"U", word[i+1:]))

                elif word[i] == u"i":
                    word = u"".join((word[:i], u"I", word[i+1:]))

        r1, r2 = self._r1r2_standard(word, self.__vowels)
        rv = self._rv_standard(word, self.__vowels)

        # STEP 0: Removal of plurals and other simplifications
        for suffix in self.__step0_suffixes:
            if word.endswith(suffix):
                if suffix in r1:
                    if suffix in (u"ul", u"ului"):
                        word = word[:-len(suffix)]

                        if suffix in rv:
                            rv = rv[:-len(suffix)]
                        else:
                            rv = u""

                    elif (suffix == u"aua" or suffix == u"atei" or
                          (suffix == u"ile" and word[-5:-3] != u"ab")):
                        word = word[:-2]

                    elif suffix in (u"ea", u"ele", u"elor"):
                        word = u"".join((word[:-len(suffix)], u"e"))

                        if suffix in rv:
                            rv = u"".join((rv[:-len(suffix)], u"e"))
                        else:
                            rv = u""

                    elif suffix in (u"ii", u"iua", u"iei",
                                    u"iile", u"iilor", u"ilor"):
                        word = u"".join((word[:-len(suffix)], u"i"))

                        if suffix in rv:
                            rv = u"".join((rv[:-len(suffix)], u"i"))
                        else:
                            rv = u""

                    elif suffix in (u"a\u0163ie", u"a\u0163ia"):
                        word = word[:-1]
                break

        # STEP 1: Reduction of combining suffixes
        while True:

            replacement_done = False

            for suffix in self.__step1_suffixes:
                if word.endswith(suffix):
                    if suffix in r1:
                        step1_success = True
                        replacement_done = True

                        if suffix in (u"abilitate", u"abilitati",
                                      u"abilit\u0103i", 
                                      u"abilit\u0103\u0163i"):
                            word = u"".join((word[:-len(suffix)], u"abil"))

                        elif suffix == u"ibilitate":
                            word = word[:-5]

                        elif suffix in (u"ivitate", u"ivitati", 
                                        u"ivit\u0103i",
                                        u"ivit\u0103\u0163i"):
                            word = u"".join((word[:-len(suffix)], u"iv"))

                        elif suffix in (u"icitate", u"icitati", u"icit\u0103i",
                                        u"icit\u0103\u0163i", u"icator",
                                        u"icatori", u"iciv", u"iciva", 
                                        u"icive", u"icivi", u"iciv\u0103", 
                                        u"ical", u"icala", u"icale", u"icali",
                                        u"ical\u0103"):
                            word = u"".join((word[:-len(suffix)], u"ic"))

                        elif suffix in (u"ativ", u"ativa", u"ative", u"ativi",
                                        u"ativ\u0103", u"a\u0163iune", 
                                        u"atoare", u"ator", u"atori", 
                                        u"\u0103toare",
                                        u"\u0103tor", u"\u0103tori"):
                            word = u"".join((word[:-len(suffix)], u"at"))

                            if suffix in r2:
                                r2 = u"".join((r2[:-len(suffix)], u"at"))

                        elif suffix in (u"itiv", u"itiva", u"itive", u"itivi",
                                        u"itiv\u0103", u"i\u0163iune", 
                                        u"itoare", u"itor", u"itori"):
                            word = u"".join((word[:-len(suffix)], u"it"))

                            if suffix in r2:
                                r2 = u"".join((r2[:-len(suffix)], u"it"))
                    else:
                        step1_success = False
                    break

            if not replacement_done:
                break

        # STEP 2: Removal of standard suffixes
        for suffix in self.__step2_suffixes:
            if word.endswith(suffix):
                if suffix in r2:
                    step2_success = True

                    if suffix in (u"iune", u"iuni"):
                        if word[-5] == u"\u0163":
                            word = u"".join((word[:-5], u"t"))

                    elif suffix in (u"ism", u"isme", u"ist", u"ista", u"iste",
                                    u"isti", u"ist\u0103", u"i\u015Fti"):
                        word = u"".join((word[:-len(suffix)], u"ist"))

                    else:
                        word = word[:-len(suffix)]
                break

        # STEP 3: Removal of verb suffixes
        if not step1_success and not step2_success:
            for suffix in self.__step3_suffixes:
                if word.endswith(suffix):
                    if suffix in rv:
                        if suffix in (u'seser\u0103\u0163i', u'seser\u0103m',
                                      u'ser\u0103\u0163i', u'sese\u015Fi',
                                      u'seser\u0103', u'ser\u0103m', u'sesem',
                                      u'se\u015Fi', u'ser\u0103', u'sese',
                                      u'a\u0163i', u'e\u0163i', u'i\u0163i',
                                      u'\xE2\u0163i', u'sei', u'\u0103m', 
                                      u'em', u'im', u'\xE2m', u'se'):
                            word = word[:-len(suffix)]
                            rv = rv[:-len(suffix)]
                        else:
                            if (not rv.startswith(suffix) and
                                rv[rv.index(suffix)-1] not in
                                u"aeio\u0103\xE2\xEE"):
                                word = word[:-len(suffix)]
                        break

        # STEP 4: Removal of final vowel
        for suffix in (u"ie", u"a", u"e", u"i", u"\u0103"):
            if word.endswith(suffix):
                if suffix in rv:
                    word = word[:-len(suffix)]
                break

        word = word.replace(u"I", u"i").replace(u"U", u"u")


        return word


class RussianStemmer(SnowballStemmer):
    """The Russian Snowball stemmer.

    @cvar __perfective_gerund_suffixes: Suffixes to be deleted.
    @type __perfective_gerund_suffixes: C{tuple}
    @cvar __adjectival_suffixes: Suffixes to be deleted.
    @type __adjectival_suffixes: C{tuple}
    @cvar __reflexive_suffixes: Suffixes to be deleted.
    @type __reflexive_suffixes: C{tuple}
    @cvar __verb_suffixes: Suffixes to be deleted.
    @type __verb_suffixes: C{tuple}
    @cvar __noun_suffixes: Suffixes to be deleted.
    @type __noun_suffixes: C{tuple}
    @cvar __superlative_suffixes: Suffixes to be deleted.
    @type __superlative_suffixes: C{tuple}
    @cvar __derivational_suffixes: Suffixes to be deleted.
    @type __derivational_suffixes: C{tuple}
    @note: A detailed description of the Russian
           stemming algorithm can be found under
           U{http://snowball.tartarus.org/algorithms
           /russian/stemmer.html}.

    """

    zope.interface.implements(interfaces.IRussianStemmer)

    __perfective_gerund_suffixes = (u"ivshis'", u"yvshis'", u"vshis'", 
                                      u"ivshi", u"yvshi", u"vshi", u"iv", 
                                      u"yv", u"v")
    __adjectival_suffixes = (u'ui^ushchi^ui^u', u'ui^ushchi^ai^a', 
                               u'ui^ushchimi', u'ui^ushchymi', u'ui^ushchego', 
                               u'ui^ushchogo', u'ui^ushchemu', u'ui^ushchomu', 
                               u'ui^ushchikh', u'ui^ushchykh', 
                               u'ui^ushchui^u', u'ui^ushchaia', 
                               u'ui^ushchoi^u', u'ui^ushchei^u', 
                               u'i^ushchi^ui^u', u'i^ushchi^ai^a', 
                               u'ui^ushchee', u'ui^ushchie', 
                               u'ui^ushchye', u'ui^ushchoe', u'ui^ushchei`', 
                               u'ui^ushchii`', u'ui^ushchyi`', 
                               u'ui^ushchoi`', u'ui^ushchem', u'ui^ushchim', 
                               u'ui^ushchym', u'ui^ushchom', u'i^ushchimi', 
                               u'i^ushchymi', u'i^ushchego', u'i^ushchogo', 
                               u'i^ushchemu', u'i^ushchomu', u'i^ushchikh', 
                               u'i^ushchykh', u'i^ushchui^u', u'i^ushchai^a', 
                               u'i^ushchoi^u', u'i^ushchei^u', u'i^ushchee', 
                               u'i^ushchie', u'i^ushchye', u'i^ushchoe', 
                               u'i^ushchei`', u'i^ushchii`', 
                               u'i^ushchyi`', u'i^ushchoi`', u'i^ushchem', 
                               u'i^ushchim', u'i^ushchym', u'i^ushchom', 
                               u'shchi^ui^u', u'shchi^ai^a', u'ivshi^ui^u', 
                               u'ivshi^ai^a', u'yvshi^ui^u', u'yvshi^ai^a', 
                               u'shchimi', u'shchymi', u'shchego', u'shchogo', 
                               u'shchemu', u'shchomu', u'shchikh', u'shchykh', 
                               u'shchui^u', u'shchai^a', u'shchoi^u', 
                               u'shchei^u', u'ivshimi', u'ivshymi', 
                               u'ivshego', u'ivshogo', u'ivshemu', u'ivshomu', 
                               u'ivshikh', u'ivshykh', u'ivshui^u', 
                               u'ivshai^a', u'ivshoi^u', u'ivshei^u', 
                               u'yvshimi', u'yvshymi', u'yvshego', u'yvshogo', 
                               u'yvshemu', u'yvshomu', u'yvshikh', u'yvshykh', 
                               u'yvshui^u', u'yvshai^a', u'yvshoi^u', 
                               u'yvshei^u', u'vshi^ui^u', u'vshi^ai^a', 
                               u'shchee', u'shchie', u'shchye', u'shchoe', 
                               u'shchei`', u'shchii`', u'shchyi`', u'shchoi`', 
                               u'shchem', u'shchim', u'shchym', u'shchom', 
                               u'ivshee', u'ivshie', u'ivshye', u'ivshoe', 
                               u'ivshei`', u'ivshii`', u'ivshyi`', 
                               u'ivshoi`', u'ivshem', u'ivshim', u'ivshym', 
                               u'ivshom', u'yvshee', u'yvshie', u'yvshye', 
                               u'yvshoe', u'yvshei`', u'yvshii`', 
                               u'yvshyi`', u'yvshoi`', u'yvshem', 
                               u'yvshim', u'yvshym', u'yvshom', u'vshimi', 
                               u'vshymi', u'vshego', u'vshogo', u'vshemu', 
                               u'vshomu', u'vshikh', u'vshykh', u'vshui^u', 
                               u'vshai^a', u'vshoi^u', u'vshei^u', 
                               u'emi^ui^u', u'emi^ai^a', u'nni^ui^u', 
                               u'nni^ai^a', u'vshee', 
                               u'vshie', u'vshye', u'vshoe', u'vshei`', 
                               u'vshii`', u'vshyi`', u'vshoi`', 
                               u'vshem', u'vshim', u'vshym', u'vshom', 
                               u'emimi', u'emymi', u'emego', u'emogo', 
                               u'ememu', u'emomu', u'emikh', u'emykh', 
                               u'emui^u', u'emai^a', u'emoi^u', u'emei^u', 
                               u'nnimi', u'nnymi', u'nnego', u'nnogo', 
                               u'nnemu', u'nnomu', u'nnikh', u'nnykh', 
                               u'nnui^u', u'nnai^a', u'nnoi^u', u'nnei^u', 
                               u'emee', u'emie', u'emye', u'emoe', 
                               u'emei`', u'emii`', u'emyi`', 
                               u'emoi`', u'emem', u'emim', u'emym', 
                               u'emom', u'nnee', u'nnie', u'nnye', u'nnoe', 
                               u'nnei`', u'nnii`', u'nnyi`', 
                               u'nnoi`', u'nnem', u'nnim', u'nnym', 
                               u'nnom', u'i^ui^u', u'i^ai^a', u'imi', u'ymi', 
                               u'ego', u'ogo', u'emu', u'omu', u'ikh', 
                               u'ykh', u'ui^u', u'ai^a', u'oi^u', u'ei^u', 
                               u'ee', u'ie', u'ye', u'oe', u'ei`', 
                               u'ii`', u'yi`', u'oi`', u'em', 
                               u'im', u'ym', u'om')
    __reflexive_suffixes = (u"si^a", u"s'")
    __verb_suffixes = (u"esh'", u'ei`te', u'ui`te', u'ui^ut', 
                         u"ish'", u'ete', u'i`te', u'i^ut', u'nno', 
                         u'ila', u'yla', u'ena', u'ite', u'ili', u'yli', 
                         u'ilo', u'ylo', u'eno', u'i^at', u'uet', u'eny', 
                         u"it'", u"yt'", u'ui^u', u'la', u'na', u'li', 
                         u'em', u'lo', u'no', u'et', u'ny', u"t'", 
                         u'ei`', u'ui`', u'il', u'yl', u'im', 
                         u'ym', u'en', u'it', u'yt', u'i^u', u'i`', 
                         u'l', u'n')
    __noun_suffixes = (u'ii^ami', u'ii^akh', u'i^ami', u'ii^am', u'i^akh', 
                         u'ami', u'iei`', u'i^am', u'iem', u'akh', 
                         u'ii^u', u"'i^u", u'ii^a', u"'i^a", u'ev', u'ov', 
                         u'ie', u"'e", u'ei', u'ii', u'ei`', 
                         u'oi`', u'ii`', u'em', u'am', u'om', 
                         u'i^u', u'i^a', u'a', u'e', u'i', u'i`', 
                         u'o', u'u', u'y', u"'")
    __superlative_suffixes = (u"ei`she", u"ei`sh")
    __derivational_suffixes = (u"ost'", u"ost")

    def stem(self, word):
        """
        Stem a Russian word and return the stemmed form.
        @param word: The word that is stemmed.
        @type word: C{str, unicode}
        @return: The stemmed form.
        @rtype: C{unicode}

        """
        # don't stem stopwords. Note; we do not lower russian words for compare
        # with stopwords
        if word in self.stopwords:
            return word

        chr_exceeded = False   
        for i in xrange(len(word)):
            if ord(word[i]) not in xrange(256):
                chr_exceeded = True
                break

        if chr_exceeded:
            word = self.__cyrillic_to_roman(word)

        step1_success = False
        adjectival_removed = False
        verb_removed = False
        undouble_success = False
        superlative_removed = False

        rv, r2 = self.__regions_russian(word)

        # Step 1
        for suffix in self.__perfective_gerund_suffixes:
            if rv.endswith(suffix):
                if suffix in (u"v", u"vshi", u"vshis'"):
                    if (rv[-len(suffix)-3:-len(suffix)] == "i^a" or 
                        rv[-len(suffix)-1:-len(suffix)] == "a"):
                        word = word[:-len(suffix)]
                        r2 = r2[:-len(suffix)]
                        rv = rv[:-len(suffix)]
                        step1_success = True
                        break
                else:
                    word = word[:-len(suffix)]
                    r2 = r2[:-len(suffix)]
                    rv = rv[:-len(suffix)]
                    step1_success = True
                    break

        if not step1_success:
            for suffix in self.__reflexive_suffixes:
                if rv.endswith(suffix):
                    word = word[:-len(suffix)]
                    r2 = r2[:-len(suffix)]
                    rv = rv[:-len(suffix)]
                    break

            for suffix in self.__adjectival_suffixes:
                if rv.endswith(suffix):
                    if suffix in (u'i^ushchi^ui^u', u'i^ushchi^ai^a', 
                              u'i^ushchui^u', u'i^ushchai^a', u'i^ushchoi^u', 
                              u'i^ushchei^u', u'i^ushchimi', u'i^ushchymi', 
                              u'i^ushchego', u'i^ushchogo', u'i^ushchemu', 
                              u'i^ushchomu', u'i^ushchikh', u'i^ushchykh', 
                              u'shchi^ui^u', u'shchi^ai^a', u'i^ushchee', 
                              u'i^ushchie', u'i^ushchye', u'i^ushchoe', 
                              u'i^ushchei`', u'i^ushchii`', u'i^ushchyi`', 
                              u'i^ushchoi`', u'i^ushchem', u'i^ushchim', 
                              u'i^ushchym', u'i^ushchom', u'vshi^ui^u', 
                              u'vshi^ai^a', u'shchui^u', u'shchai^a', 
                              u'shchoi^u', u'shchei^u', u'emi^ui^u', 
                              u'emi^ai^a', u'nni^ui^u', u'nni^ai^a', 
                              u'shchimi', u'shchymi', u'shchego', u'shchogo', 
                              u'shchemu', u'shchomu', u'shchikh', u'shchykh', 
                              u'vshui^u', u'vshai^a', u'vshoi^u', u'vshei^u', 
                              u'shchee', u'shchie', u'shchye', u'shchoe', 
                              u'shchei`', u'shchii`', u'shchyi`', u'shchoi`', 
                              u'shchem', u'shchim', u'shchym', u'shchom', 
                              u'vshimi', u'vshymi', u'vshego', u'vshogo', 
                              u'vshemu', u'vshomu', u'vshikh', u'vshykh', 
                              u'emui^u', u'emai^a', u'emoi^u', u'emei^u', 
                              u'nnui^u', u'nnai^a', u'nnoi^u', u'nnei^u', 
                              u'vshee', u'vshie', u'vshye', u'vshoe', 
                              u'vshei`', u'vshii`', u'vshyi`', u'vshoi`', 
                              u'vshem', u'vshim', u'vshym', u'vshom', 
                              u'emimi', u'emymi', u'emego', u'emogo', 
                              u'ememu', u'emomu', u'emikh', u'emykh', 
                              u'nnimi', u'nnymi', u'nnego', u'nnogo', 
                              u'nnemu', u'nnomu', u'nnikh', u'nnykh', 
                              u'emee', u'emie', u'emye', u'emoe', u'emei`', 
                              u'emii`', u'emyi`', u'emoi`', u'emem', u'emim', 
                              u'emym', u'emom', u'nnee', u'nnie', u'nnye', 
                              u'nnoe', u'nnei`', u'nnii`', u'nnyi`', u'nnoi`', 
                              u'nnem', u'nnim', u'nnym', u'nnom'):
                        if (rv[-len(suffix)-3:-len(suffix)] == "i^a" or 
                            rv[-len(suffix)-1:-len(suffix)] == "a"):
                            word = word[:-len(suffix)]
                            r2 = r2[:-len(suffix)]
                            rv = rv[:-len(suffix)]
                            adjectival_removed = True
                            break
                    else:
                        word = word[:-len(suffix)]
                        r2 = r2[:-len(suffix)]
                        rv = rv[:-len(suffix)]
                        adjectival_removed = True
                        break

            if not adjectival_removed:
                for suffix in self.__verb_suffixes:
                    if rv.endswith(suffix):
                        if suffix in (u"la", u"na", u"ete", u"i`te", u"li", 
                                      u"i`", u"l", u"em", u"n", u"lo", u"no", 
                                      u"et", u"i^ut", u"ny", u"t'", u"esh'", 
                                      u"nno"):
                            if (rv[-len(suffix)-3:-len(suffix)] == "i^a" or 
                                rv[-len(suffix)-1:-len(suffix)] == "a"):
                                word = word[:-len(suffix)]
                                r2 = r2[:-len(suffix)]
                                rv = rv[:-len(suffix)]
                                verb_removed = True
                                break
                        else:
                            word = word[:-len(suffix)]
                            r2 = r2[:-len(suffix)]
                            rv = rv[:-len(suffix)]
                            verb_removed = True
                            break

            if not adjectival_removed and not verb_removed:
                for suffix in self.__noun_suffixes:
                    if rv.endswith(suffix):
                        word = word[:-len(suffix)]
                        r2 = r2[:-len(suffix)]
                        rv = rv[:-len(suffix)]
                        break

        # Step 2
        if rv.endswith("i"):
            word = word[:-1]
            r2 = r2[:-1]

        # Step 3
        for suffix in self.__derivational_suffixes:
            if r2.endswith(suffix):
                word = word[:-len(suffix)]
                break

        # Step 4
        if word.endswith("nn"):
            word = word[:-1]
            undouble_success = True

        if not undouble_success:
            for suffix in self.__superlative_suffixes:
                if word.endswith(suffix):
                    word = word[:-len(suffix)]
                    superlative_removed = True
                    break
            if word.endswith("nn"):
                word = word[:-1]

        if not undouble_success and not superlative_removed:
            if word.endswith("'"):
                word = word[:-1]

        if chr_exceeded:
            word = self.__roman_to_cyrillic(word)

        return word

    def __regions_russian(self, word):
        """
        Return the regions RV and R2 which are used by the Russian stemmer.

        In any word, RV is the region after the first vowel, 
        or the end of the word if it contains no vowel.

        R2 is the region after the first non-vowel following 
        a vowel in R1, or the end of the word if there is no such non-vowel.

        R1 is the region after the first non-vowel following a vowel, 
        or the end of the word if there is no such non-vowel.

        @param word: The Russian word whose regions RV and R2 are determined.
        @type word: C{str, unicode}
        @return: C{(rv, r2)}, the regions RV and R2 for the 
                 respective Russian word.
        @rtype: C{tuple}
        @note: This helper method is invoked by the stem method of the subclass
               L{RussianStemmer}. It is not to be invoked directly!

        """
        r1 = u""
        r2 = u""
        rv = u""

        vowels = (u"A", u"U", u"E", u"a", u"e", u"i", u"o", u"u", u"y")
        word = (word.replace(u"i^a", u"A")
                    .replace(u"i^u", u"U")
                    .replace(u"e`", u"E"))

        for i in xrange(1, len(word)):
            if word[i] not in vowels and word[i-1] in vowels:
                r1 = word[i+1:]
                break

        for i in xrange(1, len(r1)):
            if r1[i] not in vowels and r1[i-1] in vowels:
                r2 = r1[i+1:]
                break

        for i in xrange(len(word)):
            if word[i] in vowels:
                rv = word[i+1:]
                break

        r2 = (r2.replace(u"A", u"i^a")
                .replace(u"U", u"i^u")
                .replace(u"E", u"e`"))
        rv = (rv.replace(u"A", u"i^a")
              .replace(u"U", u"i^u")
              .replace(u"E", u"e`"))

        return (rv, r2)


    def __cyrillic_to_roman(self, word):
        """
        Transliterate a Russian word into the Roman alphabet.

        A Russian word whose letters consist of the Cyrillic
        alphabet are transliterated into the Roman alphabet
        in order to ease the forthcoming stemming process.

        @param word: The word that is transliterated.
        @type word: C{unicode}
        @return: C{word}, the transliterated word.
        @rtype: C{unicode}
        @note: This helper method is invoked by the stem method of the subclass
               L{RussianStemmer}. It is not to be invoked directly!

        """
        word = (word.replace(u"\u0410", u"a").replace(u"\u0430", u"a")
                    .replace(u"\u0411", u"b").replace(u"\u0431", u"b")
                    .replace(u"\u0412", u"v").replace(u"\u0432", u"v")
                    .replace(u"\u0413", u"g").replace(u"\u0433", u"g")
                    .replace(u"\u0414", u"d").replace(u"\u0434", u"d")
                    .replace(u"\u0415", u"e").replace(u"\u0435", u"e")
                    .replace(u"\u0401", u"e").replace(u"\u0451", u"e")
                    .replace(u"\u0416", u"zh").replace(u"\u0436", u"zh")
                    .replace(u"\u0417", u"z").replace(u"\u0437", u"z")
                    .replace(u"\u0418", u"i").replace(u"\u0438", u"i")
                    .replace(u"\u0419", u"i`").replace(u"\u0439", u"i`")
                    .replace(u"\u041A", u"k").replace(u"\u043A", u"k")
                    .replace(u"\u041B", u"l").replace(u"\u043B", u"l")
                    .replace(u"\u041C", u"m").replace(u"\u043C", u"m")
                    .replace(u"\u041D", u"n").replace(u"\u043D", u"n")
                    .replace(u"\u041E", u"o").replace(u"\u043E", u"o")
                    .replace(u"\u041F", u"p").replace(u"\u043F", u"p")
                    .replace(u"\u0420", u"r").replace(u"\u0440", u"r")
                    .replace(u"\u0421", u"s").replace(u"\u0441", u"s")
                    .replace(u"\u0422", u"t").replace(u"\u0442", u"t")
                    .replace(u"\u0423", u"u").replace(u"\u0443", u"u")
                    .replace(u"\u0424", u"f").replace(u"\u0444", u"f")
                    .replace(u"\u0425", u"kh").replace(u"\u0445", u"kh")
                    .replace(u"\u0426", u"t^s").replace(u"\u0446", u"t^s")
                    .replace(u"\u0427", u"ch").replace(u"\u0447", u"ch")
                    .replace(u"\u0428", u"sh").replace(u"\u0448", u"sh")
                    .replace(u"\u0429", u"shch").replace(u"\u0449", u"shch")
                    .replace(u"\u042A", u"''").replace(u"\u044A", u"''")
                    .replace(u"\u042B", u"y").replace(u"\u044B", u"y")
                    .replace(u"\u042C", u"'").replace(u"\u044C", u"'")
                    .replace(u"\u042D", u"e`").replace(u"\u044D", u"e`")
                    .replace(u"\u042E", u"i^u").replace(u"\u044E", u"i^u")
                    .replace(u"\u042F", u"i^a").replace(u"\u044F", u"i^a"))

        return word

    def __roman_to_cyrillic(self, word):
        """
        Transliterate a Russian word back into the Cyrillic alphabet.

        A Russian word formerly transliterated into the Roman alphabet
        in order to ease the stemming process, is transliterated back
        into the Cyrillic alphabet, its original form.

        @param word: The word that is transliterated.
        @type word: C{str, unicode}
        @return: C{word}, the transliterated word.
        @rtype: C{unicode}
        @note: This helper method is invoked by the stem method of the subclass
               L{RussianStemmer}. It is not to be invoked directly!

        """
        word = (word.replace(u"i^u", u"\u044E").replace(u"i^a", u"\u044F")
                    .replace(u"shch", u"\u0449").replace(u"kh", u"\u0445")
                    .replace(u"t^s", u"\u0446").replace(u"ch", u"\u0447")
                    .replace(u"e`", u"\u044D").replace(u"i`", u"\u0439")
                    .replace(u"sh", u"\u0448").replace(u"k", u"\u043A")
                    .replace(u"e", u"\u0435").replace(u"zh", u"\u0436")
                    .replace(u"a", u"\u0430").replace(u"b", u"\u0431")
                    .replace(u"v", u"\u0432").replace(u"g", u"\u0433")
                    .replace(u"d", u"\u0434").replace(u"e", u"\u0435")
                    .replace(u"z", u"\u0437").replace(u"i", u"\u0438")
                    .replace(u"l", u"\u043B").replace(u"m", u"\u043C")
                    .replace(u"n", u"\u043D").replace(u"o", u"\u043E")
                    .replace(u"p", u"\u043F").replace(u"r", u"\u0440")
                    .replace(u"s", u"\u0441").replace(u"t", u"\u0442")
                    .replace(u"u", u"\u0443").replace(u"f", u"\u0444")
                    .replace(u"''", u"\u044A").replace(u"y", u"\u044B")
                    .replace(u"'", u"\u044C"))

        return word


class SpanishStemmer(_StandardStemmer):
    """The Spanish Snowball stemmer.

    @cvar __vowels: The Spanish vowels.
    @type __vowels: C{unicode}
    @cvar __step0_suffixes: Suffixes to be deleted in step 0 of the algorithm.
    @type __step0_suffixes: C{tuple}
    @cvar __step1_suffixes: Suffixes to be deleted in step 1 of the algorithm.
    @type __step1_suffixes: C{tuple}
    @cvar __step2a_suffixes: Suffixes to be deleted in step 2a of the algorithm.
    @type __step2a_suffixes: C{tuple}
    @cvar __step2b_suffixes: Suffixes to be deleted in step 2b of the algorithm.
    @type __step2b_suffixes: C{tuple}
    @cvar __step3_suffixes: Suffixes to be deleted in step 3 of the algorithm.
    @type __step3_suffixes: C{tuple}
    @note: A detailed description of the Spanish
           stemming algorithm can be found under
           U{http://snowball.tartarus.org/algorithms
           /spanish/stemmer.html}.

    """

    zope.interface.implements(interfaces.ISpanishStemmer)

    __vowels = u"aeiou\xE1\xE9\xED\xF3\xFA\xFC"
    __step0_suffixes = (u"selas", u"selos", u"sela", u"selo", u"las",
                        u"les", u"los", u"nos", u"me", u"se", u"la", u"le", 
                        u"lo")
    __step1_suffixes = (u'amientos', u'imientos', u'amiento', u'imiento',
                        u'aciones', u'uciones', u'adoras', u'adores',
                        u'ancias', u'log\xEDas', u'encias', u'amente',
                        u'idades', u'anzas', u'ismos', u'ables', u'ibles',
                        u'istas', u'adora', u'aci\xF3n', u'antes', 
                        u'ancia', u'log\xEDa', u'uci\xf3n', u'encia', 
                        u'mente', u'anza', u'icos', u'icas', u'ismo', 
                        u'able', u'ible', u'ista', u'osos', u'osas', 
                        u'ador', u'ante', u'idad', u'ivas', u'ivos', 
                        u'ico',
                        u'ica', u'oso', u'osa', u'iva', u'ivo')
    __step2a_suffixes = (u'yeron', u'yendo', u'yamos', u'yais', u'yan', 
                         u'yen', u'yas', u'yes', u'ya', u'ye', u'yo', 
                         u'y\xF3')
    __step2b_suffixes = (u'ar\xEDamos', u'er\xEDamos', u'ir\xEDamos',
                         u'i\xE9ramos', u'i\xE9semos', u'ar\xEDais',
                         u'aremos', u'er\xEDais', u'eremos', 
                         u'ir\xEDais', u'iremos', u'ierais', u'ieseis', 
                         u'asteis', u'isteis', u'\xE1bamos', 
                         u'\xE1ramos', u'\xE1semos', u'ar\xEDan', 
                         u'ar\xEDas', u'ar\xE9is', u'er\xEDan', 
                         u'er\xEDas', u'er\xE9is', u'ir\xEDan', 
                         u'ir\xEDas', u'ir\xE9is',
                         u'ieran', u'iesen', u'ieron', u'iendo', u'ieras',
                         u'ieses', u'abais', u'arais', u'aseis', 
                         u'\xE9amos', u'ar\xE1n', u'ar\xE1s', 
                         u'ar\xEDa', u'er\xE1n', u'er\xE1s', 
                         u'er\xEDa', u'ir\xE1n', u'ir\xE1s',
                         u'ir\xEDa', u'iera', u'iese', u'aste', u'iste',
                         u'aban', u'aran', u'asen', u'aron', u'ando', 
                         u'abas', u'adas', u'idas', u'aras', u'ases', 
                         u'\xEDais', u'ados', u'idos', u'amos', u'imos', 
                         u'emos', u'ar\xE1', u'ar\xE9', u'er\xE1', 
                         u'er\xE9', u'ir\xE1', u'ir\xE9', u'aba', 
                         u'ada', u'ida', u'ara', u'ase', u'\xEDan', 
                         u'ado', u'ido', u'\xEDas', u'\xE1is', 
                         u'\xE9is', u'\xEDa', u'ad', u'ed', u'id', 
                         u'an', u'i\xF3', u'ar', u'er', u'ir', u'as', 
                         u'\xEDs', u'en', u'es')
    __step3_suffixes = (u"os", u"a", u"e", u"o", u"\xE1",
                        u"\xE9", u"\xED", u"\xF3")

    def stem(self, word):
        """
        Stem a Spanish word and return the stemmed form.

        @param word: The word that is stemmed.
        @type word: C{str, unicode}
        @return: The stemmed form.
        @rtype: C{unicode}

        """
        # lower, since all the rules are lower-cased
        word = word.lower()
        # don't stem stopwords
        if word in self.stopwords:
            return word

        step1_success = False

        r1, r2 = self._r1r2_standard(word, self.__vowels)
        rv = self._rv_standard(word, self.__vowels)

        # STEP 0: Attached pronoun
        for suffix in self.__step0_suffixes:
            if word.endswith(suffix):
                if rv.endswith(suffix):
                    if rv[:-len(suffix)].endswith((u"i\xE9ndo", 
                                                   u"\xE1ndo",
                                                   u"\xE1r", u"\xE9r",
                                                   u"\xEDr")):
                        word = (word[:-len(suffix)].replace(u"\xE1", u"a")
                                                   .replace(u"\xE9", u"e")
                                                   .replace(u"\xED", u"i"))
                        r1 = (r1[:-len(suffix)].replace(u"\xE1", u"a")
                                               .replace(u"\xE9", u"e")
                                               .replace(u"\xED", u"i"))
                        r2 = (r2[:-len(suffix)].replace(u"\xE1", u"a")
                                               .replace(u"\xE9", u"e")
                                               .replace(u"\xED", u"i"))
                        rv = (rv[:-len(suffix)].replace(u"\xE1", u"a")
                                               .replace(u"\xE9", u"e")
                                               .replace(u"\xED", u"i"))

                    elif rv[:-len(suffix)].endswith((u"ando", u"iendo",
                                                     u"ar", u"er", u"ir")):
                        word = word[:-len(suffix)]
                        r1 = r1[:-len(suffix)]
                        r2 = r2[:-len(suffix)]
                        rv = rv[:-len(suffix)]

                    elif (rv[:-len(suffix)].endswith(u"yendo") and
                          word[:-len(suffix)].endswith(u"uyendo")):
                        word = word[:-len(suffix)]
                        r1 = r1[:-len(suffix)]
                        r2 = r2[:-len(suffix)]
                        rv = rv[:-len(suffix)]
                break

        # STEP 1: Standard suffix removal
        for suffix in self.__step1_suffixes:
            if word.endswith(suffix):
                if suffix == u"amente" and r1.endswith(suffix):
                    step1_success = True
                    word = word[:-6]
                    r2 = r2[:-6]
                    rv = rv[:-6]

                    if r2.endswith(u"iv"):
                        word = word[:-2]
                        r2 = r2[:-2]
                        rv = rv[:-2]

                        if r2.endswith(u"at"):
                            word = word[:-2]
                            rv = rv[:-2]

                    elif r2.endswith((u"os", u"ic", u"ad")):
                        word = word[:-2]
                        rv = rv[:-2]

                elif r2.endswith(suffix):
                    step1_success = True
                    if suffix in (u"adora", u"ador", u"aci\xF3n", u"adoras",
                                  u"adores", u"aciones", u"ante", u"antes",
                                  u"ancia", u"ancias"):
                        word = word[:-len(suffix)]
                        r2 = r2[:-len(suffix)]
                        rv = rv[:-len(suffix)]

                        if r2.endswith(u"ic"):
                            word = word[:-2]
                            rv = rv[:-2]

                    elif suffix in (u"log\xEDa", u"log\xEDas"):
                        word = word.replace(suffix, u"log")
                        rv = rv.replace(suffix, u"log")

                    elif suffix in (u"uci\xF3n", u"uciones"):
                        word = word.replace(suffix, u"u")
                        rv = rv.replace(suffix, u"u")

                    elif suffix in (u"encia", u"encias"):
                        word = word.replace(suffix, u"ente")
                        rv = rv.replace(suffix, u"ente")

                    elif suffix == u"mente":
                        word = word[:-5]
                        r2 = r2[:-5]
                        rv = rv[:-5]

                        if r2.endswith((u"ante", u"able", u"ible")):
                            word = word[:-4]
                            rv = rv[:-4]

                    elif suffix in (u"idad", u"idades"):
                        word = word[:-len(suffix)]
                        r2 = r2[:-len(suffix)]
                        rv = rv[:-len(suffix)]

                        for pre_suff in (u"abil", u"ic", u"iv"):
                            if r2.endswith(pre_suff):
                                word = word[:-len(pre_suff)]
                                rv = rv[:-len(pre_suff)]

                    elif suffix in (u"ivo", u"iva", u"ivos", u"ivas"):
                        word = word[:-len(suffix)]
                        r2 = r2[:-len(suffix)]
                        rv = rv[:-len(suffix)]
                        if r2.endswith(u"at"):
                            word = word[:-2]
                            rv = rv[:-2]
                    else:
                        word = word[:-len(suffix)]
                        rv = rv[:-len(suffix)]
                break

        # STEP 2a: Verb suffixes beginning 'y'
        if not step1_success:
            for suffix in self.__step2a_suffixes:
                if (rv.endswith(suffix) and
                    word[-len(suffix)-1:-len(suffix)] == u"u"):
                    word = word[:-len(suffix)]
                    rv = rv[:-len(suffix)]
                    break

        # STEP 2b: Other verb suffixes
            for suffix in self.__step2b_suffixes:
                if rv.endswith(suffix):
                    if suffix in (u"en", u"es", u"\xE9is", u"emos"):
                        word = word[:-len(suffix)]
                        rv = rv[:-len(suffix)]

                        if word.endswith(u"gu"):
                            word = word[:-1]

                        if rv.endswith(u"gu"):
                            rv = rv[:-1]
                    else:
                        word = word[:-len(suffix)]
                        rv = rv[:-len(suffix)]
                    break

        # STEP 3: Residual suffix
        for suffix in self.__step3_suffixes:
            if rv.endswith(suffix):
                if suffix in (u"e", u"\xE9"):
                    word = word[:-len(suffix)]
                    rv = rv[:-len(suffix)]

                    if word[-2:] == u"gu" and rv[-1] == u"u":
                        word = word[:-1]
                else:
                    word = word[:-len(suffix)]
                break

        word = (word.replace(u"\xE1", u"a").replace(u"\xE9", u"e")
                    .replace(u"\xED", u"i").replace(u"\xF3", u"o")
                    .replace(u"\xFA", u"u"))


        return word


class SwedishStemmer(_ScandinavianStemmer):
    """The Swedish Snowball stemmer.

    @cvar __vowels: The Swedish vowels.
    @type __vowels: C{unicode}
    @cvar __s_ending: Letters that may directly appear before a word final 's'.
    @type __s_ending: C{unicode}
    @cvar __step1_suffixes: Suffixes to be deleted in step 1 of the algorithm.
    @type __step1_suffixes: C{tuple}
    @cvar __step2_suffixes: Suffixes to be deleted in step 2 of the algorithm.
    @type __step2_suffixes: C{tuple}
    @cvar __step3_suffixes: Suffixes to be deleted in step 3 of the algorithm.
    @type __step3_suffixes: C{tuple}
    @note: A detailed description of the Swedish
           stemming algorithm can be found under
           U{http://snowball.tartarus.org/algorithms
           /swedish/stemmer.html}.

    """

    zope.interface.implements(interfaces.ISwedishStemmer)

    __vowels = u"aeiouy\xE4\xE5\xF6"
    __s_ending = u"bcdfghjklmnoprtvy"
    __step1_suffixes = (u"heterna", u"hetens", u"heter", u"heten",
                        u"anden", u"arnas", u"ernas", u"ornas", u"andes",
                        u"andet", u"arens", u"arna", u"erna", u"orna",
                        u"ande", u"arne", u"aste", u"aren", u"ades",
                        u"erns", u"ade", u"are", u"ern", u"ens", u"het",
                        u"ast", u"ad", u"en", u"ar", u"er", u"or", u"as",
                        u"es", u"at", u"a", u"e", u"s")
    __step2_suffixes = (u"dd", u"gd", u"nn", u"dt", u"gt", u"kt", u"tt")
    __step3_suffixes = (u"fullt", u"l\xF6st", u"els", u"lig", u"ig")

    def stem(self, word):
        """
        Stem a Swedish word and return the stemmed form.

        @param word: The word that is stemmed.
        @type word: C{str, unicode}
        @return: The stemmed form.
        @rtype: C{unicode}

        """
        # lower, since all the rules are lower-cased
        word = word.lower()
        # don't stem stopwords
        if word in self.stopwords:
            return word

        r1 = self._r1_scandinavian(word, self.__vowels)

        # STEP 1
        for suffix in self.__step1_suffixes:
            if r1.endswith(suffix):
                if suffix == u"s":
                    if word[-2] in self.__s_ending:
                        word = word[:-1]
                        r1 = r1[:-1]
                else:
                    word = word[:-len(suffix)]
                    r1 = r1[:-len(suffix)]
                break

        # STEP 2
        for suffix in self.__step2_suffixes:
            if r1.endswith(suffix):
                word = word[:-1]
                r1 = r1[:-1]
                break

        # STEP 3
        for suffix in self.__step3_suffixes:
            if r1.endswith(suffix):
                if suffix in (u"els", u"lig", u"ig"):
                    word = word[:-len(suffix)]
                elif suffix in (u"fullt", u"l\xF6st"):
                    word = word[:-1]
                break


        return word
