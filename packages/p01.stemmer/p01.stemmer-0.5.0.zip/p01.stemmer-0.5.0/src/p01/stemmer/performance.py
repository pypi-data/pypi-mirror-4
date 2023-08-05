# -*- coding: utf-8 -*-
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
"""
$Id: performance.py 3473 2012-11-22 13:54:35Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import time

import p01.stemmer.api


###############################################################################
#
# test helper
#
###############################################################################

timeResult = None

def timeTest(function, repeatTimes=10000, *args, **kw):
    """timer"""
    res = []
    append = res.append
    def wrapper(*args, **kw):
        start_time = time.time()
        for i in range(repeatTimes):
            append(function(*args, **kw))
        total_time = time.time() - start_time
        global timeResult
        timeResult = total_time
        return res
    return wrapper(*args, **kw)


TEXT_SHORT = u"Hier kommt ein einfacher Text welcher zum Testen verwendet wird"

TEXT_LONG  = u"""Creative Commons Corporation ist keine Anwaltskanzlei und
bietet keine rechtlichen Auskünfte bzw. Dienstleistungen an. Die Verbreitung
dieser Lizenz führt nicht zu einem Mandatsverhältnis des Empfängers mit
Creative Commons.
Commons übernimmt keine Gewähr für die zur Verfügung gestellten Informationen
und lehnt jegliche Haftung für Schäden ab, die aus dem Gebrauch dieser
Informationen erwachsen. Dieser Ausschluss von Gewährleistung und Haftung
erstreckt sich auch auf die Personen, die an der Adaptierung des vorliegenden
Lizenztexts ans schweizerische Recht mitgewirkt haben.
Lizenz
Der "
Lizenzgeber", d.h. die Person, welche den Lizenzgegenstand unter dieser Lizenz
zur Verfügung stellt, und "Sie", d.h. die Person, welche aus dieser Lizenz
Nutzungsrechte ableitet,
vereinbaren mit dieser Creative Commons Public Licence ("CCPL" oder "Lizenz")
die Nutzungsbedingungen für den Lizenzgegenstand,
im Einzelnen:
1.  Definitionen
a.   "Lizenzgegenstand"
 kann ein urheberrechtlich geschütztes Werk sein oder eine durch verwandte
 Schutzrechte geschützte Leistung;
b.   ein "Sammelwerk"
 im Sinne dieser Lizenz ist eine Zusammenstellung des Lizenzgegenstands mit
 Werken oder sonstigen Elementen. Beim Sammelwerk sind Auswahl und Zusammenstellung als solche selbständig urheberrechtlich geschützt. Ein Sammelwerk gilt nicht als Werk zweiter Hand gemäss Ziff. 1 lit. c dieser Lizenz;
c.   ein "Werk zweiter Hand"
 im Sinne dieser Lizenz ist eine geistige Schöpfung mit individuellem
 Charakter, die unter Verwendung des Lizenzgegenstands so geschaffen wird,
 dass der Lizenzgegenstand in seinem individuellen Charakter erkennbar bleibt;
d.    "Urheber"
 ist, wer das Werk geschaffen hat;
e.   ein "Werk"
 ist eine geistige Schöpfung mit individuellem Charakter;
f.    ein "verwandtes Schutzrecht"
 ist ein Recht an einer kulturellen Leistung, welche nicht als Werk geschützt
 ist, wie etwa jene von ausübenden Künstlern, Herstellern von Ton- und
 Tonbildträgern oder Sendeunternehmen;
g.   "Lizenzelemente"
 sind die folgenden Lizenzcharakteristika: 
"Namensnennung", "Weitergabe-unter-gleichen-Bedingungen", "Keine Bearbeitung",
"Nicht-kommerziell". Sie werden vom Lizenzgeber ausgewählt und in der
Bezeichnung dieser Lizenz soweit anwendbar genannt.
2.   Schranken des Urheberrechts. Dieser Lizenzvertrag lässt sämtliche
Befugnisse unberührt, die sich aufgrund der Beschränkungen der
ausschliesslichen Rechte des Rechtsinhabers durch das Urheberrechtsgesetz
(Eigengebrauch, Erschöpfungsgrundsatz etc.) oder durch andere Bestimmungen
der anwendbaren Gesetzgebung ergeben.
3.   Lizenzierung. Unter den Bestimmungen dieser Lizenz räumt Ihnen der
Lizenzgeber die Befugnis ein, den Lizenzgegenstand weltweit,
lizenzgebührenfrei, nicht exklusiv und zeitlich unbeschränkt (d.h. für die
Schutzdauer des Werks oder des verwandten Schutzrechts) wie folgt zu nutzen:
a.   den Lizenzgegenstand zu vervielfältigen, ihn in ein oder mehrere
Sammelwerke aufzunehmen und ihn im Rahmen des Sammelwerks zu vervielfältigen;
b.   den Lizenzgegenstand zu bearbeiten oder in anderer Weise umzugestalten;
c.   den Lizenzgegenstand oder Vervielfältigungen davon zu verbreiten,
öffentlich wiederzugeben, durch Radio, Fernsehen oder ähnliche Einrichtungen,
auch über Leitungen, zu senden, weiterzusenden oder sonstwie wahrnehmbar zu
machen, wobei sich diese Befugnisse auch auf den in ein Sammelwerk
aufgenommenen Lizenzgegenstand erstrecken;
d.   den bearbeiteten oder umgestalteten Lizenzgegenstand zu vervielfältigen,
verbreiten, öffentlich wiederzugeben, durch Radio, Fernsehen oder ähnliche
Einrichtungen, auch über Leitungen, zu senden, weiterzusenden oder sonstwie
wahrnehmbar zu machen.
Die vorstehend genannten Befugnisse können für alle Nutzungsarten sowie in
jedem Medium und Format ausgeübt werden, ob diese bereits bekannt sind oder
erst in Zukunft entwickelt werden. Diese Befugnisse umfassen auch das Recht
zu Änderungen, die technisch notwendig sind, um die Befugnisse in anderen
Medien und Formaten auszuüben.
Diese Lizenz entbindet Sie nicht davon, allfällige nach dem anwendbaren Gesetz
oder Nutzungstarif geschuldeten Vergütungen zu bezahlen.
4.   Bedingungen. Die in Ziff. 3 eingeräumten Befugnisse unterliegen den
folgenden Bedingungen:
a.   Die Ausübung eines Rechts aus dieser Lizenz muss von einer Kopie dieser
Lizenz begleitet sein. Sie können davon absehen, wenn Sie anstatt dessen die
jedermann zugängliche Fundstelle dieser Lizenz bekannt geben (Uniform Resource
Identifier, URI). Sie müssen alle Hinweise auf diese Lizenz und auf ihre
Klauseln betreffend Gewährleistungs- und Haftungsausschluss beibehalten. Sie
dürfen keine Vereinbarungen treffen, welche die Bedingungen dieser Lizenz
verändern oder die mit dieser Lizenz gewährten Rechte für einen Dritten
einschränken. Sie dürfen für den Lizenzgegenstand keine Unterlizenz erteilen.
Sie dürfen den Lizenzgegenstand nicht mit technischen Schutzmassnahmen
versehen, die den Gebrauch des Lizenzgegenstands oder den Zugang zu diesem in
einer Weise kontrollieren, die mit den Bedingungen dieser Lizenz im
Widerspruch stehen.
Das Vorstehende gilt auch, falls der Lizenzgegenstand Bestandteil eines
Sammelwerks oder einer Datenbank ist. Dies bedeutet allerdings nicht, dass
das Sammelwerk oder die Datenbank als solche diesen Lizenzbestimmungen
unterstellt werden müssen.
Wenn Sie den Lizenzgegenstand in ein Sammelwerk oder eine Datenbank aufnehmen,
müssen Sie auf erste Anzeige des Urhebers oder jedes Lizenzgebers hin jeden
Hinweis auf den Anzeigenden soweit machbar und gewünscht aus dem Sammelwerk
bzw. der Datenbank entfernen; soweit Hinweise gestützt auf eine solche Anzeige
zu entfernen sind, entfallen die Pflichten gemäss Ziff. 4 lit. b.
Entsprechendes gilt bei Schöpfung eines Werks zweiter Hand.
b.   Bei der Nutzung des Lizenzgegenstands oder eines Werks zweiter Hand,
sei es isoliert oder als Teil eines Sammelwerks oder einer Datenbank, müssen
Sie die bestehenden Copyright-Vermerke vollständig beibehalten bzw. in einem
Rahmen wiedergeben, der dem technischen Verfahren und dem Trägermedium der von
Ihnen vorgenommenen Nutzung angemessen ist. Insbesondere müssen Sie den Namen
(oder das Pseudonym) des Urhebers sowie den Namen von Dritten nennen, die ein
Lizenzgeber bzw. ein Urheber in den Copyright-Vermerk aufgenommen haben. Ist
Ihnen der Titel des Lizenzgegenstands bekannt, müssen Sie diesen angeben. Hat
der Lizenzgeber eine Internetadresse angegeben (z.B. in Form des Uniform
Resource Identifier, URI), welche Lizenzinformationen oder Copyright-Vermerke
enthält, müssen Sie diese ebenfalls nennen, soweit dies mit angemessenem
Aufwand durchführbar ist.
Bei Werken zweiter Hand müssen Sie einen Hinweis darauf anführen, in welcher
Form der Lizenzgegenstand in die Bearbeitung eingegangen ist (z. B. "
Französische Übersetzung des ...
 (Werk) durch ...
 (Urheber)"
 oder "
Das Drehbuch beruht auf dem Werk des ...
 (Urheber)"
). Diese Hinweise können in jeder angemessenen Weise erfolgen. Bei Werken
zweiter Hand, Sammelwerken oder Datenbanken müssen solche Hinweise hinsichtlich
Platzierung und Ausgestaltung mindestens ebenso auffällig und in vergleichbarer
Weise ausgeführt werden, wie dies für die anderen Rechtsinhaber erfolgte.
c.   Obwohl die in Ziff. 3 eingeräumten Befugnisse nach Massgabe dieser Lizenz
ausgeübt werden dürfen, findet diese Erlaubnis ihre gesetzliche Grenze in den
Persönlichkeitsrechten der Urheber und ausübenden Künstler, deren berechtigte
geistige und persönliche Interessen bzw. deren Ansehen oder Ruf durch die
Nutzung nicht beeinträchtigt werden dürfen.
5.   Keine Gewährleistung. Sofern vom Lizenzgeber nicht schriftlich anders
anerkannt, übernimmt der Lizenzgeber keine Gewährleistung für die erteilten
Befugnisse.
6.   Haftungsausschluss. Über die in Ziff. 5 genannte Gewährleistung hinaus
haftet der Lizenzgeber nur für Vorsatz und grobe Fahrlässigkeit. Jede andere
Haftung ist ausgeschlossen, soweit gesetzlich zulässig. Für seine Hilfspersonen
haftet der Lizenzgeber in keinem Fall. Dieser Haftungsausschluss gilt auch
dann, wenn Sie auf die Möglichkeit einer Schädigung hingewiesen haben.
7.   Beendigung
a.   Diese Lizenz und die darunter eingeräumten Befugnisse fallen ohne weiteres
und mit sofortiger Wirkung dahin, wenn Sie die Bedingungen dieser Lizenz
verletzen. Die Ziffern 1, 2, 5, 6, 7 und 8 bleiben ungeachtet der Beendigung
dieser Lizenz verbindlich.
b.   Die mit dieser Lizenz eingeräumten Befugnisse werden zeitlich
uneingeschränkt eingeräumt (freilich höchstens für die Dauer, für welche der
Lizenzgegenstand nach dem anwendbaren Recht urheber- bzw.
leistungsschutzrechtlich geschützt ist). Der Lizenzgeber behält sich jedoch
für einen beliebigen Zeitpunkt das Recht vor, den Lizenzgegenstand unter einer
anderen Lizenz weiterzugeben oder die Verbreitung des Lizenzgegenstands ganz zu
beenden. Der Lizenzwechsel wird jedoch nicht die Wirkung eines Widerrufs dieser
Lizenz haben (oder jeder anderen Lizenzierung, die auf der Grundlage dieser
Lizenz erfolgt oder erfolgen muss), vielmehr wird die Lizenz so lange weiter
bestehen, als sie nicht nach lit. a vorstehend beendigt wurde.
8.  Verschiedenes
a.   Jedes Mal, wenn Sie den Lizenzgegenstand oder ein Sammelwerk gestützt auf
Ziff. 3 dieser Lizenz nutzen, räumt der Lizenzgeber auch dem Empfänger eines
allfälligen Vervielfältigungsstücks eine Lizenz am Lizenzgegenstand selber
ein, und zwar zu denselben Bedingungen wie die Ihnen eingeräumte Lizenz.
b.   Jedes Mal, wenn Sie ein Werk zweiter Hand gestützt auf Ziff. 3 dieser
Lizenz nutzen, räumt der Lizenzgeber dem Empfänger eines
Vervielfältigungsstücks eine Lizenz am Lizenzgegenstand selber ein, und zwar
zu denselben Bedingungen wie die Ihnen eingeräumte Lizenz.
c.   Sollten sich einzelne Bestimmungen dieser Lizenz nach dem anwendbaren
Recht als nicht durchsetzbar oder nichtig erweisen, so bleiben die übrigen
Bestimmungen dieser Lizenz gültig und durchsetzbar und an die Stelle der
unwirksamen Bestimmung tritt eine Ersatzregelung, die dem mit der unwirksamen
Bestimmung angestrebten Zweck am nächsten kommt.
d.   Keine Bestimmung dieser Lizenz gilt als wegbedungen und keine Verletzung
als genehmigt, bevor nicht die durch die Wegbedingung oder Genehmigung
belastete Partei die Wegbedingung oder Genehmigung in Schriftform und
unterschriftlich bestätigt hat.
e.   Diese Lizenz enthält alle mit Blick auf den Lizenzgegenstand zwischen
den Parteien massgeblichen Bestimmungen. Andere Vertrauenspositionen, Abreden
oder Zusicherungen im Hinblick auf den Lizenzgegenstand bestehen nicht. Der
Lizenzgeber ist durch keine zusätzliche Klausel gebunden, welche sich aus
irgendwelchen Unterlagen von Ihnen ergibt. Diese Vereinbarung kann ohne
vorherige Vereinbarung mit unterschriftlicher Bestätigung zwischen dem
Lizenzgeber und Ihnen nicht abgeändert werden.
f.    Auf diesen Lizenzvertrag findet ausschliesslich schweizerisches Recht
Anwendung.
Creative Commons ist nicht Partei dieses Lizenzvertrags und macht keinerlei
Zusicherungen mit Blick auf den Lizenzgegenstand. Creative Commons haftet
nicht für Ihnen entstandene Schäden aus der Verwendung des Lizenzgegenstands
oder dieser Lizenz, aus welchem Rechtsgrund sie auch abgeleitet werden, sei
es für direkten, indirekten Schaden oder für Folgeschaden. Ungeachtet des
vorstehenden Satzes hat Creative Commons alle Rechte aus dieser Lizenz,
sofern sie bezüglich eines Werks ausdrücklich selber als Lizenzgeberin unter
dieser Lizenz auftritt.
Ausser für den begrenzten Zweck, dem Publikum öffentlich bekannt zu machen,
dass der Lizenzgegenstand unter der CCPL lizenziert ist, darf keine Partei
dieser Lizenz das Markenzeichen "Creative Commons" oder irgend ein anderes
Markenzeichen oder Logo von Creative Commons ohne die vorgängige schriftliche
Zustimmung von Creative Commons verwenden. Jegliche erlaubte Nutzung hat in
Übereinstimmung mit den dannzumal gültigen Markenrichtlinien von Creative
Commons zu stehen. Die Markenrichtlinien von Creative Commons sind auf ihrer
Website abrufbar oder erhältlich auf Anfrage.   
Creative Commons kann unter http://creativecommons.org kontaktiert werden.   
"""

###############################################################################
#
# test methods
#
###############################################################################


def guessLocale(txt):
    return p01.stemmer.api.guessLocale(txt)

def doTokenize(txt, stopwords):
    return p01.stemmer.api.doTokenize(txt, stopwords)

def getStopWords(locale):
    return p01.stemmer.api.getStopWords(locale)

def stem(txt, locale, stopwords):
    # stemmer does not need stopwords because we remove them before we stem
    stemmer = p01.stemmer.api.getStemmer(locale, stopwords)
    words = [stemmer.stem(word)
             for word in p01.stemmer.api.doTokenize(txt, stopwords)]
    return u' '.join(words)


###############################################################################
#
# performance test
#
###############################################################################

def runTest(typ, repeatTimes):
    if typ == 'short':
        txt = TEXT_SHORT
    elif typ == 'long':
        txt = TEXT_LONG
    else:
        raise ValueError("No text found for given type")
    # setup stopwords
    locale = 'de'
    stopwords = p01.stemmer.api.getStopWords(locale)

    print "repeat %i times" % repeatTimes

    # start test
    timeTest(doTokenize, repeatTimes, txt, stopwords)
    print "  doTokenize:   %.2f s" % timeResult

    timeTest(guessLocale, repeatTimes, txt)
    print "  guessLocale:  %.2f s" % timeResult

    timeTest(getStopWords, repeatTimes, locale)
    print "  getStopWords: %.2f s" % timeResult

    timeTest(stem, repeatTimes, txt, locale, stopwords)
    print "  stem:         %.2f s" % timeResult

    print ""
    

def main():
    print ""
    print "run with SHORT text"
    print "-------------------"
    # short text
    runTest('short', 1)
    runTest('short', 10)
    runTest('short', 100)
    runTest('short', 1000)
    # long text
    print ""
    print "run with LONG text"
    print "------------------"
    runTest('long', 1)
    runTest('long', 10)
    runTest('long', 100)
    runTest('long', 1000)