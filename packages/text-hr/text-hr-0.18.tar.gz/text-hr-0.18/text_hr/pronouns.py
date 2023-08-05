# coding=utf-8

import codecs
from morphs import WordSuffixes, WordForms
import base
import adjectives


if not base.is_word_type_registred("PRON.OSO"):
    # TODO: vrste zamjenica - attrs_fix = službi u rečenici (imenične, pridjevne), 
    #       značenju (osobne, posvojne, povratne, povratno-posvojne, upitno odnosne i neodređene
    # base.ATTR_PRON_TYPE=="OSO" 
    # NOTE: pronouns are so much different between diff pron. subtypes, so I must define for each 
    #       distinct pronoun one special type
    PRONOUNS_OSO = base.ChangeableWordType("PRON.OSO", "Zamjenice osobne", attrs_fix=[base.ATTR_NUMBER, base.ATTR_PERSON_MFN], 
                             attrs_ch=[base.ATTR_DECLINATION], allow_duplicate_words=True) #base.ATTR_GENDER, base.ATTR_NUMBER
    # base.ATTR_PRON_TYPE=="POV" 
    PRONOUNS_POV = base.ChangeableWordType("PRON.POV", "Zamjenice.povratne", attrs_ch=[base.ATTR_DECLINATION])
    # base.ATTR_PRON_TYPE=="POS" 
    PRONOUNS_POS = base.ChangeableWordType("PRON.POS", "Zamjenice.posvojne", attrs_fix=[base.ATTR_NUMBER, base.ATTR_PERSON_MFN], 
                             attrs_ch=[base.ATTR_NUMBER, base.ATTR_DECLINATION, base.ATTR_GENDER])
    # base.ATTR_PRON_TYPE=="PPO" - svoj 
    PRONOUNS_PPO = base.ChangeableWordType("PRON.PPO", "Zamjenice.povratno-posvojne", attrs_fix=[],
                            attrs_ch=[base.ATTR_NUMBER, base.ATTR_DECLINATION, base.ATTR_GENDER])
    PRONOUNS_POK = base.ChangeableWordType("PRON.POK", "Zamjenice.pokazne", 
                            attrs_ch=[base.ATTR_NUMBER, base.ATTR_DECLINATION, base.ATTR_GENDER])
    PRONOUNS_UOD_IME = base.ChangeableWordType("PRON.UOD.IME", "Zamjenice.upitne_odnosne.imenicne", 
                                attrs_ch=[base.ATTR_NUMBER, base.ATTR_DECLINATION])
    PRONOUNS_UOD_PRD = base.ChangeableWordType("PRON.UOD.PRD", "Zamjenice.upitne_odnosne.pridjevne", 
                                attrs_ch=[base.ATTR_NUMBER, base.ATTR_DECLINATION, base.ATTR_GENDER])
    # TODO: odabrao sam po suffix-ima 
    #       trebao sam odabrati klasifikaciju po ulozi u rečenici - neodređene, niječne, opće. Osobito su niječne zanimljive
    #       ima još i klasifikacija imenične/pridjevne - može se napraviti no nisam
    #       možda bi sve trebalo kao jedan tip
    # TODO: nisam složene - barem dodati bilo, god
    # netko
    PRONOUNS_NEO_CH1  = base.ChangeableWordType("PRON.NEO.CH1", "Zamjenice.neodredjene.promjenljive", 
                                 attrs_ch=[base.ATTR_NUMBER, base.ATTR_DECLINATION])
    # neki
    PRONOUNS_NEO_CH2  = base.ChangeableWordType("PRON.NEO.CH2", "Zamjenice.neodredjene.promjenljive+spol", 
                                 attrs_ch=[base.ATTR_NUMBER, base.ATTR_DECLINATION, base.ATTR_GENDER])
    PRONOUNS_NEO_FIX = base.FixedWordType("PRON.NEO.FIX", "Zamjenice.neodredjene.nepromjenjive", 
                                          attrs_fix=[])

    # ------------------------------------------------------------ 
    # ------------------------------ OSOBNE ----------------------
    # ------------------------------------------------------------ 

    # ------------------- SUFFIXES FOR OSO - OSOBNE ZAMJENICE JA, TI, ... ----------------
    _suffixes_pron_oso_s1 = PRONOUNS_OSO.add_suffixes("S/1", "SOME", "", "", (base.ATTR_DECLINATION, ), 
                        """##   SINGULAR
                           #N   $word_base            
                           #G   e|-1
                           #D   i|-2i
                           #A   e|-1
                           #V   -
                           #L   i
                           #I   -2nom|-2nome
                        """)
    
    PRONOUNS_OSO.add_suffixes("S/2",  "SOME", "", "", suffixes_force = _suffixes_pron_oso_s1)

    _suffixes_pron_oso_s3m = PRONOUNS_OSO.add_suffixes("S/3M", "SOME", "", "", (base.ATTR_DECLINATION, ), 
                          """##   SINGULAR
                             #N   $word_base            
                             #G   a|!ga
                             #D   -1mu|!mu
                             #A   a|!ga
                             #V   -
                             #L   -1mu|-1m
                             #I   -2im|-2ime
                          """)
    PRONOUNS_OSO.add_suffixes("S/3F", "SOME", "", "", (base.ATTR_DECLINATION, ), 
                         """##   SINGULAR
                            #N   $word_base            
                            #G   -1e|!je
                            #D   j|!joj
                            #A   -2u|!ju|!je
                            #V   -
                            #L   j
                            #I   m|me
                         """)

    PRONOUNS_OSO.add_suffixes("S/3N",  "SOME", "", "", suffixes_force = _suffixes_pron_oso_s3m)

    _suffixes_pron_oso_p1 = PRONOUNS_OSO.add_suffixes("P/1", "SOME", "", "", (base.ATTR_DECLINATION, ), 
                         """##   PLURAL
                            #N   $word_base            
                            #G   -1s
                            #D   a|0
                            #A   -1s
                            #V   -
                            #L   a
                            #I   a
                         """)
    PRONOUNS_OSO.add_suffixes("P/2",  "SOME", "", "", suffixes_force = _suffixes_pron_oso_p1)

    _suffixes_pron_oso_p3m = PRONOUNS_OSO.add_suffixes("P/3M", "SOME", "", "", (base.ATTR_DECLINATION, ), 
                         """##   PLURAL
                            #N   $word_base            
                            #G   -1h|!ih
                            #D   a|!im
                            #A   -1h|!ih
                            #V   -
                            #L   a
                            #I   a
                         """)
     
    PRONOUNS_OSO.add_suffixes("P/3F",  "SOME","","", suffixes_force = _suffixes_pron_oso_p3m)
    PRONOUNS_OSO.add_suffixes("P/3N",  "SOME","","", suffixes_force = _suffixes_pron_oso_p3m)
 
    # ---------- OSOBNE - WORD FORMS -----------------

    _OSO_SUFFIX_PARAMS = (  { "lexem" : "men" , "word_base" : "ja"}
                         , { "lexem" : "teb" , "word_base" : "ti", "suffix_exceptions" : {"V" : ["$word_base"], "I" : ["!tobom"]}}
                         , { "lexem" : "njeg", "word_base" : "on"}
                         , { "lexem" : "njeg", "word_base" : "ono"}
                         # NOTE: currently this is the only case when
                         #       there are two same word_bases for same word type
                         , { "lexem" : "njo" , "word_base" : "ona"}
                         , { "lexem" : "nam" , "word_base" : "mi"}
                         , { "lexem" : "vam" , "word_base" : "vi", "suffix_exceptions" : {"V" : ["$word_base"]}}
                         , { "lexem" : "njim", "word_base" : "oni"}
                         , { "lexem" : "njim", "word_base" : "one"}
                         , { "lexem" : "njim", "word_base" : "ona"}
                        )
    i = 0
    for number in base.ATTR_NUMBER.values:
        for person in base.ATTR_PERSON_MFN.values:
            key = "%s/%s" % (number, person) 

            suffix_params = _OSO_SUFFIX_PARAMS[i]

            word_base = suffix_params["word_base"]
            word_obj = PRONOUNS_OSO.add_word(word_base)
            #import pdb;pdb.set_trace()
            suffixes = PRONOUNS_OSO.get_suffixes(key)
            suffix_exceptions =  suffix_params.get("suffix_exceptions", None)
            if suffix_exceptions:
                suffixes = PRONOUNS_OSO.add_suffixes(key, "SINGLE", word_base, 
                                              suffixes_force = suffixes.copy(name="PRON.OSO#__dummy__",
                                              exceptions = suffix_exceptions))
            word_obj.add_forms(suffix_params["lexem"], [number, person], suffixes=suffixes)
            i+=1

    # ------------------------------------------------------------ 
    # ------------------------------ POSVOJNE --------------------
    # ------------------------------------------------------------ 

    # ------------------ SUFFIXES FOR POS - POSVOJNE ZAMJENICE -----------------------
    # _suffixes_pron_oso_p3m = PRONOUNS_OSO.add_suffixes("P/3M", "SOME","","", (base.ATTR_DECLINATION, ), 
    # PRONOUNS_OSO.add_suffixes("P/3F",  "SOME","","", suffixes_force = _suffixes_pron_oso_p3m)

    _suffixes_pron_pos_s1 = PRONOUNS_POS.add_suffixes("S/1", "SOME", "moj", "",
                             (base.ATTR_NUMBER, base.ATTR_DECLINATION, base.ATTR_GENDER), 
                        """##   SINGULAR
                           ##   M                  F       N
                           ##   ----------------   ------- ---------------------
                           #N   0                  a       e
                           #G   eg|ega|-1g|-1ga    e       eg|ega|-1g|-1ga
                           #D   em|emu|-1m         oj      em|emu|-1m|-1mu
                           #A   eg|ega|-1g|-1ga|0  u       e
                           #V   0                  a       e
                           #L   em|-1m|-1mu        oj      em|-1m|-1me
                           #I   im                 om      im

                           ##   PLURAL
                           #N   i                  e       a
                           #G   ih                 ih      ih
                           #D   im|ima             im|ima  im|ima
                           #A   e                  e       a
                           #V   i                  e       a
                           #L   im|ima             im|ima  im|ima
                           #I   im|ima             im|ima  im|ima
                        """)
    _suffixes_adj_pos_neo = adjectives.WORD_TYPE.get_suffixes("P_N")

    PRONOUNS_POS.add_suffixes("S/2",  "SOME", "tvoj",   "", suffixes_force = _suffixes_pron_pos_s1)
    PRONOUNS_POS.add_suffixes("S/3M", "SOME", "njegov", "", suffixes_force = _suffixes_adj_pos_neo)
    PRONOUNS_POS.add_suffixes("S/3F", "SOME", "njezin", "", suffixes_force = _suffixes_adj_pos_neo)

    # TODO: M is pretty similar to S/1 and F and N are more similar. Union this if needed?
    _suffixes_pron_pos_p1 = PRONOUNS_POS.add_suffixes("P/1", "SOME", u"naš", "",
                             (base.ATTR_NUMBER, base.ATTR_DECLINATION, base.ATTR_GENDER), 
                        """##   SINGULAR
                           ##   M                  F       N
                           ##   ----------------   ------- ---------------------
                           #N   0                  a       e
                           #G   eg|ega             e       eg|ega
                           #D   em|emu             oj      em|emu
                           #A   eg|ega|0           u       e
                           #V   0                  a       e
                           #L   em|emu             oj      em|emu
                           #I   im                 om      im

                           ##   PLURAL
                           #N   i                  e       a
                           #G   ih                 ih      ih
                           #D   im|ima             im|ima  im|ima
                           #A   e                  e       a
                           #V   i                  e       a
                           #L   im|ima             im|ima  im|ima
                           #I   im|ima             im|ima  im|ima
                        """)
    PRONOUNS_POS.add_suffixes("P/2",  "SOME", "vaš",    "", suffixes_force = _suffixes_pron_pos_p1)
    # TODO: New rules doesn't allow to have 3 in person_3mfn attribute - so for all p/3* is p/3M
    PRONOUNS_POS.add_suffixes("P/3M",  "SOME", "njihov", "", suffixes_force = _suffixes_adj_pos_neo)

    # ---------- POSVOJNE - WORD FORMS -----------------
    POS_SUFFIX_PARAMS = (  { "lexem" : "moj"  , "word_base" : "ja"}
                         , { "lexem" : "tvoj" , "word_base" : "ti"}
                         , { "lexem" : "njegov" , "word_base" : "on"}
                         , { "lexem" : "njezin" , "word_base" : "ona"}
                         # plural
                         , { "lexem" : "naš" , "word_base" : "mi"}
                         , { "lexem" : "vaš" , "word_base" : "vi"}
                         , { "lexem" : "njihov" , "word_base" : "oni"}
                        )
    # WORDS["PRON.POS"]["S/1"] = WordForms("PRON.POS", "ja", "moj" , ["S", "1"], SUFFIXES["PRON.POS"]["S/1"], word_base_lexem_match=False)
    # WORDS["PRON.POS"]["S/2"] = WordForms("PRON.POS", "ti", "tvoj", ["S", "2"], SUFFIXES["PRON.POS"]["S/2"], word_base_lexem_match=False)

    i = 0
    for number in base.ATTR_NUMBER.values:
        for person in base.ATTR_PERSON_MFN.values:
            key = "%s/%s" % (number, person) 
            if person.startswith("3"):
                if key not in ("S/3M","S/3F","P/3M"):
                    continue
                # if key=="P/3M":
                #    key="P/3"
                #    person="3"
            suffix_params = POS_SUFFIX_PARAMS[i]
            assert not suffix_params.get("suffix_exceptions", None)
            word_obj = PRONOUNS_POS.add_word(suffix_params["word_base"])
            suffixes = PRONOUNS_POS.get_suffixes(key)
            word_obj.add_forms(suffix_params["lexem"], [number, person], suffixes=suffixes)
            i+=1

    # ------------------------------------------------------------ 
    # ------------------------------ POVRATNE -----------
    # ------------------------------------------------------------ 

    # --------------- SUFFIXES - POVRATNE ---------------
    _suffixes_pron_pov = PRONOUNS_POV.add_suffixes("", "SINGLE", "", "", (base.ATTR_DECLINATION, ), 
                        """##   SINGULAR
                           #N   -
                           #G   e|-2e
                           #D   i|-2i
                           #A   e|-2e
                           #V   -
                           #L   i
                           #I   -2obom
                        """)
    word_obj = PRONOUNS_POV.add_word("sebe")
    word_obj.add_forms("seb", (), suffixes=_suffixes_pron_pov)
    # ------------------------------------------------------------ 
    # ------------------------------ POVRATNO POSVOJNE -----------
    # ------------------------------------------------------------ 
    _suffixes_pron_ppo = PRONOUNS_PPO.add_suffixes("", "SINGLE", "", 
                            "", suffixes_force=_suffixes_pron_pos_s1)
    word_obj = PRONOUNS_PPO.add_word("svoj")
    word_obj.add_forms("svoj", (), suffixes=_suffixes_pron_ppo)
    # ------------------------------------------------------------ 
    # ------------------------------ POKAZNE -----------
    # ------------------------------------------------------------ 
    _suffixes_pron_pok_ovaj = PRONOUNS_POK.add_suffixes("", "SINGLE", "ovaj", "",
                                (base.ATTR_NUMBER, base.ATTR_DECLINATION, base.ATTR_GENDER), 
                        """##   SINGULAR
                           ##   M                  F       N
                           ##   ----------------   ------- ---------------------
                           #N   $word_base             a       o
                           #G   og|oga             e       og|oga       
                           #D   om|omu             oj      om|omu       
                           #A   og|oga|$word_base      u       o
                           #V   -                  -       -            
                           #L   om|ome             oj      om|ome       
                           #I   im|ime             om      im|ime       
                                                                        
                           ##   PLURAL                     PLURAL
                           #N   i                  e       a            
                           #G   ih                 ih      ih           
                           #D   im|ima             im|ima  im|ima       
                           #A   e                  e       a            
                           #V   -                  -       -            
                           #L   im|ima             im|ima  im|ima       
                           #I   im|ima             im|ima  im|ima       
                        """)
    # TODO: This is dictionary of diff words, how to diff this from dict of same word diff fix attrs??
    #       new class for first or another??
    _word_ovaj = PRONOUNS_POK.add_word("ovaj")
    _word_ovaj.add_forms("ov", (), suffixes=_suffixes_pron_pok_ovaj)

    _word_taj  = PRONOUNS_POK.add_word("taj")
    _word_taj.add_forms("t", (), suffixes=_suffixes_pron_pok_ovaj)

    _word_onaj = PRONOUNS_POK.add_word("onaj")
    _word_onaj.add_forms("on", (), suffixes=_suffixes_pron_pok_ovaj)
 
   # TODO: union i nepostojano a
   # NOTE: This was not good: 
    _suffixes_adj_pos_neo_odr = adjectives.WORD_TYPE.get_suffixes("P_N+O")
    _suffixes_pron_pok_ovakav = PRONOUNS_POK.add_suffixes("", "SINGLE", "ovakav", 
                                    "", suffixes_force = _suffixes_adj_pos_neo_odr.copy(name="PRON.POK#__dummy__",
                                                           exceptions={"S/A/M" : ["a", "oga", "og"]}))
    # TODO: for lexem - probably %A could serve
    for line in ("ovakav %A", "takav %A", "ovolik ovolik", "tolik tolik", "onolik onolik"):
        word_base, lexem = line.split()
        _word = PRONOUNS_POK.add_word(word_base)
        _word.add_forms(lexem, (), suffixes=_suffixes_pron_pok_ovakav)

    # ------------------------------------------------------------ 
    # ------------------------------ UPITNE/ODNOSNE  -----------
    # ------------------------------------------------------------ 

    # imenične
    _suffixes_pron_uod_ime_tko = PRONOUNS_UOD_IME.add_suffixes("", "SOME", "tko", "",
                (base.ATTR_NUMBER, base.ATTR_DECLINATION, ), 
                        """##   SINGULAR
                           ##   M               
                           ##   ----------------
                           #N   $word_base          
                           #G   ga          
                           #D   m|mu          
                           #A   ga
                           #V   -               
                           #L   m|me          
                           #I   -1im|-1ime          
                           ## PLURAL
                           #N   -
                           #G   -
                           #D   -
                           #A   -
                           #V   -               
                           #L   -
                           #I   -
                        """)

    _word_tko = PRONOUNS_UOD_IME.add_word("tko")
    _word_tko.add_forms("ko", (), _suffixes_pron_uod_ime_tko)

    _suffixes_pron_uod_ime_sto = PRONOUNS_UOD_IME.add_suffixes("", "SOME", u"što", 
                        "", suffixes_force = _suffixes_pron_uod_ime_tko.copy(name=u"PRON.UOD.IME#__dummy__", 
                                                  exceptions={"S/D" : ["mu"], "S/L" : ["m", "mu"]}))
    _word_sto = PRONOUNS_UOD_IME.add_word(u"što")
    _word_sto.add_forms("če", (), _suffixes_pron_uod_ime_sto)

    # pridjevne

    _suffixes_pron_uod_prd_koji = PRONOUNS_UOD_PRD.add_suffixes("", "SOME", "koji", "",
                    (base.ATTR_NUMBER, base.ATTR_DECLINATION, base.ATTR_GENDER), 
                        """##   SINGULAR
                           ##   M                  F       N
                           ##   ----------------   ------- ---------------------
                           #N   $word_base             a       e
                           #G   eg|ega             e       eg|ega       
                           #D   em|emu             oj      em|emu       
                           #A   eg|ega|$word_base      u       e
                           #V   -                  -       -            
                           #L   em                 oj      em
                           #I   im|ime             om      im
                                                                        
                           ##   PLURAL                     PLURAL
                           #N   i                  e       a            
                           #G   ih                 ih      ih           
                           #D   im|ima             im|ima  im|ima       
                           #A   e                  e       a            
                           #V   -                  -       -            
                           #L   im|ima             im|ima  im|ima       
                           #I   im|ima             im|ima  im|ima       
                        """)
    # TODO: This is dictionary of diff words, how to diff this from dict of same word diff fix attrs??
    #       new class for first or another??
    _word_koji = PRONOUNS_UOD_PRD.add_word(u"koji")
    _word_koji.add_forms("koj", (), _suffixes_pron_uod_prd_koji)

    _word_ciji = PRONOUNS_UOD_PRD.add_word(u"čiji")
    _word_ciji.add_forms(u"čij", (), _suffixes_pron_uod_prd_koji)

    # s = adjectives.SUFFIXES["ADJ"]["P_N+O"]
    _suffixes_pron_uod_prd_kakav = PRONOUNS_UOD_IME.add_suffixes("", "SOME", u"kakav", 
                        "", suffixes_force = _suffixes_adj_pos_neo_odr.copy(name=u"PRON.UOD.PRD#__dummy__", 
                                               exceptions={"S/A/M" : ["a", "oga", "og"]}))
    _word_kakav = PRONOUNS_UOD_PRD.add_word(u"kakav")
    _word_kakav.add_forms(u"%A", (), _suffixes_pron_uod_prd_kakav)

    _word_kolik = PRONOUNS_UOD_PRD.add_word(u"kolik")
    _word_kolik.add_forms(u"kolik", (), _suffixes_adj_pos_neo_odr)

    # ---------------------
    _suffixes_pron_neo_ch2_sav = PRONOUNS_NEO_CH2.add_suffixes("", "SINGLE", "sav", "",
                             (base.ATTR_NUMBER, base.ATTR_DECLINATION, base.ATTR_GENDER), 
                            """##   SINGULAR
                               ##   M                  F       N
                               ##   ----------------   ------- ---------------------
                               #N   %A0                a       e
                               #G   ega|eg             e       ega|eg
                               #D   emu|em             oj      emu|em
                               #A   ega|eg|%A0         u       e
                               #V   %A0                a       e
                               #L   em|emu             oj      em|emu
                               #I   im|ime             om      im|ime

                               ##   PLURAL
                               #N   i                  e       a
                               #G   ih                 ih|iju  ih
                               #D   im|ima             im|ima  im|ima
                               #A   e                  e       a
                               #V   i                  e       a
                               #L   im|ima             im|ima  im|ima
                               #I   im|ima             im|ima  im|ima
                            """)


    _WS_PRON_FIX_WORDS = set()

    # NOTE: unicode issues
    for i, word_base in enumerate(u"""netko nešto neki nekakav nečiji
                    gdjetko gdješto gdjekoji gdjekakav
                    tkogod štogod kojigod kakavgod čijigod

                    nitko ništa ničiji nikakav

                    itko išta ikoji ikakav
                    svatko svašta svaki svačiji svakakav sav
                    kojetko koješta kojekakav
                    """.split()):
        word_base = word_base.lower().strip()
        if not word_base:
            continue
        changeable=True
        word_base_lexem_match = False
        lexem = None
        suffixes = None
        word_base_utf8 = codecs.encode(word_base, "utf-8")
        word_type_str = "PRON.NEO.CH1"
        if word_base in ("neki", "svaki"):
            word_type_str = "PRON.NEO.CH2"
            lexem = word_base[:-1]
            suffixes = adjectives.WORD_TYPE.get_suffixes("P_O")
            word_base_lexem_match = True
        elif word_base in ("sav", ):
            word_type_str = "PRON.NEO.CH2"
            suffixes = _suffixes_pron_neo_ch2_sav
            lexem = "sv"
        elif word_base.endswith("god"):
            changeable=False
            # TODO: needs new type
        elif word_base.endswith("tko"):
            lexem = word_base[:-len("tko")]+"ko"
            # NOTE: this shouldn't be corrected, since nekog belongs to neki
            suffixes = _suffixes_pron_uod_ime_tko 
        elif word_base[-3:] in (u"što", u"šta"):
            lexem = word_base[:-len(u"što")]+u"če"
            suffixes = _suffixes_pron_uod_ime_sto 
        elif word_base[-4:] in (u"koji", u"čiji"):
            word_type_str = "PRON.NEO.CH2"
            lexem = word_base[:-1]
            # TODO: solve this unicode and similar stuff
            base_word_base = codecs.encode(word_base[-4:], "utf-8")
            #suffixes = WORDS["PRON.UOD.PRD"][base_word_base].suffixes
            suffixes = _suffixes_pron_uod_prd_koji 
            word_base_lexem_match = True
        elif word_base[-5:] in ("kolik", "kakav"):
            word_type_str = "PRON.NEO.CH2"
            if word_base[-5:] in ("kolik", ):
                suffixes = _suffixes_adj_pos_neo_odr
                word_base_lexem_match = True
                lexem = word_base
            elif word_base[-5:] in ("kakav", ):
                # TODO: Probably this will work too: lexem = "%A"
                suffixes = _suffixes_pron_uod_prd_kakav
                lexem, suffix = WordSuffixes.remove_vc_A(word_base, "")
            base_word_base = word_base[-5:]
            #suffixes = WORDS["PRON.UOD.PRD"][base_word_base].suffixes
        else:
            raise Exception("for word_base '%s' not found class" % word_base)
        if suffixes:
            assert lexem, word_base
            # print i, word_base, lexem, changeable, suffixes, word_base_lexem_match
            word_obj = base.get_word_type(word_type_str).add_word(word_base)
            word_obj.add_forms(lexem, (), suffixes)
            #WORDS[word_type_str][word_base_utf8] = WordForms(word_type_str, word_base, lexem, [], suffixes,
            #                                             word_base_lexem_match=False)
        else:
            # print i, codecs.encode(word_base, "utf-8"), "TODO: not finished"
            assert word_base_utf8 not in _WS_PRON_FIX_WORDS
            _WS_PRON_FIX_WORDS.add(word_base_utf8)

    assert len(_WS_PRON_FIX_WORDS)
    #PRONOUNS_NEO_FIX = base.WordSet("PRON.NEO.FIX", attr_to_update_values=None)
    PRONOUNS_NEO_FIX.std_words.add_set(None, " ".join(_WS_PRON_FIX_WORDS))

# ----------------------------------------------------------
else:
# ----------------------------------------------------------
    PRONOUNS_NEO_CH1  = base.get_word_type("PRON.NEO.CH1")
    PRONOUNS_NEO_CH2  = base.get_word_type("PRON.NEO.CH2")
    PRONOUNS_NEO_FIX  = base.get_word_type("PRON.NEO.FIX")
    PRONOUNS_OSO      = base.get_word_type("PRON.OSO"    )
    PRONOUNS_POK      = base.get_word_type("PRON.POK"    )
    PRONOUNS_POS      = base.get_word_type("PRON.POS"    )
    PRONOUNS_POV      = base.get_word_type("PRON.POV"    )
    PRONOUNS_PPO      = base.get_word_type("PRON.PPO"    )
    PRONOUNS_UOD_IME  = base.get_word_type("PRON.UOD.IME")
    PRONOUNS_UOD_PRD  = base.get_word_type("PRON.UOD.PRD")

WORD_TYPE = None # too many of them to say which is main
WORDS     = None # WORD_TYPE.std_words


#>>> forms, words = SUFFIXES["PRON"]_OS["S/1"].get_forms("ja", "men")
#>>> forms, words = SUFFIXES["PRON"]_OS["S/1"].get_forms("ti", "teb", {"V" : ["$word_base"], "I" : ["!tobom"]})
#>>> forms, words = SUFFIXES["PRON"]_OS["S/3M"].get_forms("on", "njeg")
#>>> forms, words = SUFFIXES["PRON"]_OS["S/3M"].get_forms("ono", "njeg")
#>>> forms, words = SUFFIXES["PRON"]_OS["S/3F"].get_forms("ona", "njo")
#>>> forms, words = SUFFIXES["PRON"]_OS["P/1"].get_forms("mi", "nam")
#>>> forms, words = SUFFIXES["PRON"]_OS["P/1"].get_forms("vi", "vam", {"V" : ["$word_base"]})
#>>> forms, words = SUFFIXES["PRON"]_OS["P/3M"].get_forms("oni", "njim")
#>>> forms, words = SUFFIXES["PRON"]_OS["P/3M"].get_forms("one", "njim")
#>>> forms, words = SUFFIXES["PRON"]_OS["P/3M"].get_forms("ona", "njim")

def test():
    print "%s: running doctests" % __name__
    import doctest
    doctest.testmod()
    base.run_doctests(( "test_pronouns.txt", ))

if __name__ == "__main__":
    test()


