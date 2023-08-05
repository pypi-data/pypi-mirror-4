# coding=utf-8
# type of words
# doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
"""
>>> import base
>>> sorted(ADVERBS.std_words.wordset.keys())        # doctest: +NORMALIZE_WHITESPACE
['KOL.KOLIKO', 'MJE.DOKLE', 'MJE.GDJE', 'MJE.KAMO', 'MJE.KUDA', 'MJE.ODKUDA',
 'NAC.KAKO', 'OST.NEOC', 'OST.OGRAN', 'OST.POUZD', 'OST.POUZD_PP', 
 'OST.POUZD_VM', 'OST.POUZD_VM_PP', 'OST.RAZN', 'OST.SUMNJ', 'OST.SUPR', 
 'POS.S_ISHOD', 'UZR.ZASTO', 'VRE.DOKAD', 'VRE.KADA', 'VRE.OTKAD']

>>> len(ADVERBS.std_words.wordset["MJE.GDJE"])
20

>>> sorted(ADVERBS.std_words.wordset.keys())==sorted(base._ATTR_LIST["ADV_T"].values)
True

>>> sorted(PREPOSITIONS.std_words.wordset.keys())        # doctest: +NORMALIZE_WHITESPACE
['UZ_A', 'UZ_D', 'UZ_G', 'UZ_I', 'UZ_L']

>>> len(PREPOSITIONS.std_words.wordset["UZ_D"])
6

>>> sorted(CONJUCTIONS.std_words.wordset.keys())        # doctest: +NORMALIZE_WHITESPACE
['NOR', 'ODZAM', 'PRI']

>>> len(CONJUCTIONS.std_words.wordset["ODZAM"])
6

>>> sorted(EXCLAMATIONS.std_words.wordset.keys())        # doctest: +NORMALIZE_WHITESPACE
['DOZ', 'ONO', 'OSJ', 'POK']

>>> len(EXCLAMATIONS.std_words.wordset["POK"])
3

>>> len(PARTICLES.std_words.words)
12

>>> print ADVERBS.std_words.pp_set("MJE.GDJE")
blizu
dolje
drugdje
gdjegdje
gore
igdje
kojegdje
negdje
nigdje
ondje
ovdje
podalje
ponegdje
postrance
sprijeda
straga
svagdje
tu
unutra
vani

>>> len(ABBREVIATIONS.std_words.words)
34

>>> ["%s" % ADVERBS.wts_list[k] for k in sorted(ADVERBS.wts_list.keys())] # doctest: +NORMALIZE_WHITESPACE
["WTS(wt=ADV,cd=u'A_?_AS',list=u'as',freq=very rare)",
"WTS(wt=ADV,cd=u'A_?_A\\\\u010cKI',list=u'a\\\\u010dki',freq=very rare)",
"WTS(wt=ADV,cd=u'A_?_CE',list=u'ce',freq=very rare)",
"WTS(wt=ADV,cd=u'A_?_ICE',list=u'ice',freq=frequent)",
"WTS(wt=ADV,cd=u'A_?_IMICE',list=u'imice',freq=frequent)",
"WTS(wt=ADV,cd=u'A_?_KE',list=u'ke',freq=frequent)",
"WTS(wt=ADV,cd=u'A_?_KI',list=u'ki',freq=frequent)",
"WTS(wt=ADV,cd=u'A_?_OS',list=u'os',freq=very rare)",
"WTS(wt=ADV,cd=u'A_?_US',list=u'us',freq=very rare)"]


"""
import base

class AdverbType(base.FixedWordType):
    def __init__(self):
        super(AdverbType, self).__init__("ADV",  "Prilozi",
                                         attrs_fix=[base.ATTR_ADV_TYPE])
        # A - iz pridjeva
        self._add_wts({"ADV_T": "?"}, "ice"  ,    2, "A", "", "danomice")
        self._add_wts({"ADV_T": "?"}, "imice",    2, "A", "", "hrpimice")
        self._add_wts({"ADV_T": "?"}, "ke"   ,    2, "A", "", "ležećke")
        self._add_wts({"ADV_T": "?"}, "ki"   ,    2, "A", "", "hodećki")
        self._add_wts({"ADV_T": "?"}, "ački" ,    0, "A", "", "glavečki")
        self._add_wts({"ADV_T": "?"}, "as"   ,    0, "A", "", "danas")
        self._add_wts({"ADV_T": "?"}, "ce"   ,    0, "A", "", "neprestance")
        self._add_wts({"ADV_T": "?"}, "os"   ,    0, "A", "", "jutros")
        self._add_wts({"ADV_T": "?"}, "us"   ,    0, "A", "", "zimus")

if not base.is_word_type_registred("ADV"):
    # unchangeable
    ADVERBS       = AdverbType()
    PREPOSITIONS  = base.FixedWordType("PREP",  "Prijedlozi",  attrs_fix=[base.ATTR_PREP_TYPE], allow_duplicate_words=True)
    CONJUCTIONS   = base.FixedWordType("CONJ", "Veznici",      attrs_fix=[base.ATTR_CONJ_TYPE])
    EXCLAMATIONS  = base.FixedWordType("EXCL", "Usklici",      attrs_fix=[base.ATTR_EXCL_TYPE], allow_duplicate_words=True)
    PARTICLES     = base.FixedWordType("PART", "Čestice")
    ABBREVIATIONS = base.FixedWordType("ABBR", "Skraćenice")
    #SUFFIXES = {}
    #WORDS    = {}

    # --------------------- PRILOZI --------------------
    # MJESNI
    #gdje - mjesto
    ADVERBS.std_words.add_set("MJE.GDJE", """ovdje tu ondje negdje nigdje gdjegdje igdje 
                                 kojegdje ponegdje svagdje gore drugdje dolje 
                                 sprijeda straga unutra vani blizu podalje 
                                 postrance""") # ...

    # #kamo - smjer u koje mjesto
    ADVERBS.std_words.add_set("MJE.KAMO", """ovamo tamo onamo nikamo nekamo ikamo drugamo 
                                      naprijed natrag van """) # ... 
    # kuda - put kojim
    ADVERBS.std_words.add_set("MJE.KUDA", """ovuda tuda onuda nikuda nekuda ikuda kojekuda 
                                      druguda
                                   """) # ... 
    #otkuda odakle
    ADVERBS.std_words.add_set("MJE.ODKUDA", """odavde odavle odovud otud odatle odonud 
                                        odande odanle niotkuda niodakle odnekud 
                                        odasvud odozgo odozdo odsprijeda odostraga 
                                        odnekle izdaleka poizdalje izbliza izbliže 
                                        izvana
                                   """) # ... 
    # dokle dokud
    ADVERBS.std_words.add_set("MJE.DOKLE", """dovle dotle donle donekle
                                    """) # ... 
    # TODO: razlikovanje (str. 158.320) - bliže gov bliže sug podalje 

    # VREMENSKI
    # kada
    # TODO: unicode
    ADVERBS.std_words.add_set("VRE.KADA", """sada tada onda nikada nekada ikada gdjekad 
                                      ponekad katkad svakad uvijek svagda prekjučer 
                                      jučer danas sutra prekosutra preklani lani 
                                      ljetos jesenas zimus proljetos preksinoć sinoć 
                                      jutros večeras noćas obdan obnoć odmah smjesta 
                                      davno često rijetko rano kasno prije poslije 
                                      pravodobno već istom tek zatim potom maločas 
                                      nedavno skoro uskoro napokon
                                    """) # ... 
    # otkad
    ADVERBS.std_words.add_set("VRE.OTKAD", """odsad otad oduvijek odavna odiskona odmalena 
                                       odskoro 
                                    """) # ... 
    # dokad
    ADVERBS.std_words.add_set("VRE.DOKAD", """dosad dotad doskoro dogodine dovečer
                                    """) # ... 
    # UZROČNI
    # zašto
    ADVERBS.std_words.add_set("UZR.ZASTO", """zato stoga
                                    """)
    # POSLJEDIČNI
    # s kojim ishodom
    ADVERBS.std_words.add_set("POS.S_ISHOD", """uzalud uaman utaman
                                      """)
    # NAČINSKI
    # kako
    ADVERBS.std_words.add_set("NAC.KAKO", """ovako tako onako nikako nekako ikako kojekako
                                      svakojako kriomice strelimice ničice nemilice 
                                      neopazice potajice poimence jatomice uzagrapce 
                                      nasumce strmoglavce četveronoške poleđuške 
                                      potrbuške naglavačke sjedečke stojećke ležećke 
                                      nauznak naopako napretrg nauštrb napamet naglas 
                                      napreskok iznenada odjednom jedva svejedno 
                                      """) # ...
    # TODO: priloz == pridjev u srednjem rodu
    # # nastali od prijedjeva (kojim načinom)
    # # poz kop superlativa opisnih pridjeva
    # blago blaže najblaže brzo daleko dalje hitro hitrije jako lako lijepo teško teže najteže tiho veselo zlo žestoko...
    # # razlika od pridjeva u srednjem rodu - prilozi kako? prilažu se glagolima
    # dijete se igra (kako?) veselo
    # # a pridjevi pobliže označuju imenicu srednjeg roda - kakvo?
    # dijete je (kakvo?) veselo

    # TODO: priloz == odnosni pridjev na -ski
    # # bratski gospodski hrvatski ljudski ...
    # # priloz odgovara na kako?
    # govorimo (kako?) hrvatski
    # # pridjev čiji? koji? kakav?
    # naš jezik je (koji?) hrvatski

    # KOLIČINSKI
    # koliko?
    ADVERBS.std_words.add_set("KOL.KOLIKO", """ovoliko toliko onoliko nekoliko ikoliko 
                                        malo premalo nimalo pomalo manje više 
                                        previše mnogo premnogo dosta odveć još 
                                        opet ponovo iznova sasvim potpuno djelomice 
                                        djelimično jedanput dvaput triput
                                     """) # ...
    # OSTALI
    # pouzdanost
    ADVERBS.std_words.add_set("OST.POUZD", """doista uistinu zaista zbilja svakako
                                    """)
    # + popriloženi pridjevi
    ADVERBS.std_words.add_set("OST.POUZD_PP", """naravno pouzdano neosporno neprijeporno
                                          nesumnjivo
                                       """)
    # veću ili manju pouzdanost
    ADVERBS.std_words.add_set("OST.POUZD_VM", """možda valjda zacijelo
                                       """)
    # + popriloženi pridjevi
    ADVERBS.std_words.add_set("OST.POUZD_VM_PP", """sigurno zasigurno jamačno vjerojatno
                                          """)
    # sumnja
    ADVERBS.std_words.add_set("OST.SUMNJ", """navodno tobože naizgled
                                    """)
    # neočekivanost
    ADVERBS.std_words.add_set("OST.NEOC", """ipak
                                     """)
    # ograničenost
    ADVERBS.std_words.add_set("OST.OGRAN", """samo
                                    """)
    # suprotnost
    ADVERBS.std_words.add_set("OST.SUPR", """međutim pak
                                   """)
    # raznovrsnost
    ADVERBS.std_words.add_set("OST.RAZN", """također isto bar baš čak 
                                   """)
    # TODO: provjeri ove: upravo najmanje štoviše

    # ---------- PRIJEDLOZI -----------------

    # TODO: mjesto, nada, pod je imenica i prijedlog (preda je glagol i prijedlog
    #       kako to razlučiti da i mjesto ne postane stopword
    PREPOSITIONS.std_words.add_set("UZ_G", """bez blizu čelo do duž ispod ispred iz iza između 
                                  iznad izvan kod kraj mjesto mimo nakon nakraj niže 
                                  od oko osim pokraj poput pored poslije preko prije
                                  protiv put radi s sa sred u umjesto uzduž van više vrh 
                                  za zbog
                               """) # ...
    PREPOSITIONS.std_words.add_set("UZ_D", """k ka suprot nasuprot unatoč usprkos
                                  """)
    PREPOSITIONS.std_words.add_set("UZ_A", """kroz među mimo na nad nada niz niza o po pod poda
                                     pred preda u uz uza za
                                  """)
    PREPOSITIONS.std_words.add_set("UZ_L", """na o po pri prema u
                                  """)
    PREPOSITIONS.std_words.add_set("UZ_I", """među nad pod poda pred preda s sa za
                                  """)
    # TODO: pravila: k/ka, s/sa - 162 str 328.
    # ---------- veznici  -----------------
    CONJUCTIONS.std_words = base.FixedWordList("CONJ", attr_to_update_values=base.ATTR_CONJ_TYPE)

    # normalni veznici
    CONJUCTIONS.std_words.add_set("NOR", """i pa te ni niti a ali nego no ili da dok jer ako 
                                 mada makar premda iako kao
                              """)
    # prilozi u službi veznika
    CONJUCTIONS.std_words.add_set("PRI", """gdje kuda kamo odakle kada otkad otkako kako dokle 
                                 pošto samo već dakle
                              """)
    # odnosne zamjenice u službi veznika
    CONJUCTIONS.std_words.add_set("ODZAM", """tko što koji čiji kakav kolik
                                """)
    # TODO: više riječi u službi veznika - str 164. 332, budući da, s obzirom na to što ...

    # ---------- USKLICI -----------------

    # osjećaji i raspoloženja
    EXCLAMATIONS.std_words.add_set("OSJ", """ah aha aj au avaj brr e eh ehe ej haj he hej hm hura 
                                 ih iju ijuju jao joj ju juh o oh oko oj pi u uh uf 
                              """) # ...
    # dozivanje i poticanje
    EXCLAMATIONS.std_words.add_set("DOZ", """de deder gic iš hajde halo hej mic na o oj šic
                              """) # ...

    #  onomatopejski 
    EXCLAMATIONS.std_words.add_set("ONO", """buć bum ćap dum hop mljac pljus tres zum
                              """) # ...
    # pokazivanje 
    EXCLAMATIONS.std_words.add_set("POK", """evo eto eno
                              """)

    # ---------- ČESTICE -----------------
    # svaka od njih ima značenje a neke su i prilozi ili neke dr. vrste riječi (put, puta, evo, eto,...)
    PARTICLES.std_words.add_set("ALL", """god put puta neka evo eto eno li zar ne da se
                             """) # ...
    
    # Skraćenice - moraš nešto imati - TODO: je li ovo uopče treba biti ovdje?? i nisu najbolje
    # TODO: check each ends with ., and what with case sensitive
    # N - before name
    ABBREVIATIONS.std_words.add_set("N",   """dr. mr. sc. gdin. gđa. 
                                              gđica. g. gosp. ing. inž. ms. mrs. 
                                              miss. mons. msgr. fra. dir. 
                                           """)
    ABBREVIATIONS.std_words.add_set("OTH", """v. r. d. npr. itd. al. 
                                              tj. eg. sv. st. 
                                              o. gl. ur. arh. tzv. usp. sl.
                                           """)


# ----------------------------------------------------------
else:
# ----------------------------------------------------------
    ADVERBS      = base.get_word_type("ADV" )
    PREPOSITIONS = base.get_word_type("PREP")
    CONJUCTIONS  = base.get_word_type("CONJ")
    EXCLAMATIONS = base.get_word_type("EXCL")
    PARTICLES    = base.get_word_type("PART")
    ABBREVIATIONS = base.get_word_type("ABBR")

def test():
    print "%s: running doctests" % __name__
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    test()
