# coding=utf-8
#...    print "%-40s " % val, # doctest: +NORMALIZE_WHITESPACE
"""
# TODO: THIS IS SLOW - enable this later

>>> from datetime import datetime, timedelta
>>> started = datetime.now()

>>> WORD_TYPE.init_wts_forms()
>>> ended = datetime.now()

Currently this takes about 1.7 sec on my machine
>>> (ended - started) < timedelta(seconds=4)
True

>>> from morphs import get_suff_registry
>>> SR = get_suff_registry()
>>> print SR
SR(1205 suffixes, 2888 SRI objects)

ex. SR(1289 suffixes, 2888 SRI objects)
"""
from text_hr.utils import to_unicode, IterAttrs

import base
from morphs import WordSuffixes, count_wparts, AEIOU, ChangeableWordBase, BadParamsInitError
from morphs import _remove_vc_a, _apply_vc_a, split_by_last_AEIOU


# ---------------------------------------

class Adjective(ChangeableWordBase):
    """
    >>> def print_it(params_init):
    ...     key = Adjective.params2key(params_init)
    ...     print repr(key), repr(Adjective.key2params(key))

    >>> print_it({})
    '$A/$N/$C/$S' {'has_neo': None, 'com_wp1_suff': None, 'apply_vc_a': None, 'has_com': None}
    >>> print_it({"apply_vc_a" : True, "has_neo" : False, "com_wp1_suff" : "iji"})
    '+A/-N/$C/ijiS' {'has_neo': False, 'com_wp1_suff': 'iji', 'apply_vc_a': True, 'has_com': None}

    Izmjenjivanje ije i je:
    >>> bijel = Adjective("bijel")
    >>> bijel.params_key, bijel.params_key
    ('+A/+N/+C/$S', '+A/+N/+C/$S')
    >>> bijel2 = Adjective("bijel", Adjective.key2params(bijel.params_key))
    >>> print bijel2
    W(u'bijel'=ADJ)
    >>> bijel2.forms["P_N/S/N/M"]
    [u'bijel']
    >>> bijel2.forms["COM/S/N/M"]
    [u'bjelji']
    
    >>> print bijel
    W(u'bijel'=ADJ)
    >>> bijel.forms["P_N/S/N/M"]
    [u'bijel']
    >>> bijel.forms["COM/S/N/M"]
    [u'bjelji']

    Nepostojano A - ok:
    >>> otporan = Adjective("otporan")
    >>> otporan[10]
    ('P_N/S/A/F', [u'otpornu'])

    >>> otporan[100]
    ('COM/S/L/F', [u'otpornijoj'])

    >>> otporan.is_better_than(otporan) is None
    Traceback (most recent call last):
        ...
        assert key1!=key2
    AssertionError

    Nepostojano A - not OK - positiv wrong, comparative is wrong:
    >>> bodljikav = Adjective("bodljikav")
    >>> bodljikav[10]
    ('P_N/S/A/F', [u'bodljikvu'])
    >>> bodljikav[100]
    ('COM/S/L/F', [u'bodljikvijoj'])

    This is good:
    >>> bodljikav = Adjective("bodljikav", apply_vc_a=False)
    >>> bodljikav[10]
    ('P_N/S/A/F', [u'bodljikavu'])
    >>> bodljikav[100]
    ('COM/S/L/F', [u'bodljikavijoj'])

    Stats introspecition:
    >>> len(bodljikav.forms_stats)
    43
    >>> wf_list = sorted(bodljikav.forms_stats.keys())
    >>> wf = wf_list[0]
    >>> wf
    u'bodljikav'
    >>> bodljikav.forms_stats[wf]
    (0, None)
    >>> wf_list[-1]
    u'najbodljikaviju'


    >>> crven = Adjective("crven")
    >>> print crven
    W(u'crven'=ADJ)

    >>> print crven.com_base, crven.com_base_ws, crven.com_lexem
    crveniji (u'crven', u'iji') crvenij

    >>> print crven.sup_base, crven.sup_base_ws, crven.sup_lexem
    najcrveniji (u'najcrven', u'iji') najcrvenij

    This is 1 wpart word for which we can't determine which is correct com ok:
    >>> AdjectiveType.get_comp_base_suff("bos")
    {(u'bo\u0161', u'i'): 0.5, (u'bos', u'iji'): 0.5}

    >>> bos = Adjective("bos") # NOTE: lazy init
    >>> bos.com_base
    Traceback (most recent call last):
        ...
    Exception: W(u'bos'=ADJ) hasn't got enough info for determining comparative word base. got: {(u'bo\u0161', u'i'): 0.5, (u'bos', u'iji'): 0.5}


    So we must pass which to use "ji" or "iji" - in this case is "iji":
    >>> bos = Adjective("bos", com_wp1_suff="iji")

    And it seems ok:
    >>> print bos.sup_base, bos.sup_base_ws, bos.sup_lexem
    najbosiji (u'najbos', u'iji') najbosij

    >>> len(crven.ATTR_VALUES_ALL), len(crven.ATTR_VALUES_NO_NEO), len(crven.ATTR_VALUES_NO_COM), len(crven.ATTR_VALUES_NO_NEO_COM)
    (168, 126, 84, 42)

    >>> len(crven.attr_values)
    168
    >>> len(crven.forms_flat)==len(crven.ATTR_VALUES_ALL)
    True

    >>> crven.forms_flat[0],crven.forms_flat[-1]
    (('P_N/S/N/M', [u'crven']), ('SUP/P/I/N', [u'najcrvenijim', u'najcrvenijima']))

    >>> print crven.forms["COM/S/N/M"]
    [u'crveniji']

    try getitem:
    with key
    >>> print bos["COM/S/I/N"]
    [u'bosijim']

    or with order nr:
    >>> print bos[0],bos[-1]
    ('P_N/S/N/M', [u'bos']) ('SUP/P/I/N', [u'najbosijim', u'najbosijima'])

    Tryout __iter__:
    >>> vals = [(k,v) for k,v in bos]
    >>> len(vals)
    168
    >>> vals[-1]
    ('SUP/P/I/N', [u'najbosijim', u'najbosijima'])

    Before were demonstrated most often case (1st case)
    when adjective can have odr.form and comp./supl.
    There are 3 more cases with variations:

    2rd case - has no neodr.form but has comp./supl.:
    -----------------------------------------------
    >>> hrvatski = Adjective("hrvatski", has_neo=False)
    >>> len(hrvatski.attr_values)
    126
    >>> print hrvatski.forms_flat[0]
    ('P_O/S/N/M', [u'hrvatski'])

    >>> print hrvatski["COM/S/I/N"]
    [u'hrvatskijim']
    >>> print hrvatski["P_N/S/N/M"]
    Traceback (most recent call last):
    ...
    KeyError: 'P_N/S/N/M'

    3rd case - has neodr.form but no comp./supl.:
    -------------------------------------------
    >>> perov = Adjective("perov", has_com=False)
    >>> len(perov.attr_values)
    84
    >>> print perov["COM/S/I/N"]
    Traceback (most recent call last):
    ...
    KeyError: 'COM/S/I/N'
    >>> print perov["P_O/S/N/M"]
    [u'perovi']

    4rd case - no neodr.form and no comp./supl.:
    ------------------------------------------
    >>> brodski = Adjective("brodski", has_neo=False, has_com=False)
    >>> len(brodski.attr_values)
    42
    >>> print brodski.forms_flat[0]
    ('P_O/S/N/M', [u'brodski'])

    >>> print brodski["COM/S/I/N"]
    Traceback (most recent call last):
    ...
    KeyError: 'COM/S/I/N'
    >>> print brodski["P_N/S/N/M"]
    Traceback (most recent call last):
    ...
    KeyError: 'P_N/S/N/M'

    But if you wanna create adjective with base that ends with AEIOU
    and has_neo=True, you will get exception:
    >>> brodski = Adjective("brodski", has_neo=True, has_com=False) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    BadParamsInitError: For u'brodski' base ends with AEIOU, so has_neo has to be False, but is True ...

    And for has_neo = False, it must end with i (P_O/N/M (ODR) first form is 'i':
    >>> Adjective("brzoalkoholan", **{'has_neo': False, 'com_wp1_suff': 'ji', 
    ... 'apply_vc_a': True, 'has_com': True}) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    BadParamsInitError: For u'brzoalkoholan' base has has_neo=False, but it doesn't end with 'i' ...

    >>> Adjective("brzoalkoholn", **{'has_neo': False, 'com_wp1_suff': 'ji', 
    ... 'apply_vc_a': True, 'has_com': True}) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    BadParamsInitError: For u'brzoalkoholn' base has has_neo=False, but it doesn't end with 'i' ...

    
    When you pass lexem - it can happen that word_base can be automatically change. 
    This is detected by very first forms_flat:
    >>> brutaln = Adjective("brutaln")
    >>> print brutaln.forms_flat[0][1]
    [u'brutalan']
    >>> print brutaln.word_base
    brutalan
    >>> print brutaln.word_base_changed
    True

    >>> achak = Adjective(unicode("ačak", "utf-8"), apply_vc_a=None, is_suffix=True)
    >>> achak.forms_flat[:10] # doctest: +NORMALIZE_WHITESPACE
    [('P_N/S/N/M', [u'a\u010dak']), ('P_N/S/N/F', [u'a\u010dka']), ('P_N/S/N/N', [u'a\u010dko']), 
     ('P_N/S/G/M', [u'a\u010dka']), ('P_N/S/G/F', [u'a\u010dke']), ('P_N/S/G/N', [u'a\u010dka']), 
     ('P_N/S/D/M', [u'a\u010dku']), ('P_N/S/D/F', [u'a\u010dkoj']), ('P_N/S/D/N', [u'a\u010dku']), 
     ('P_N/S/A/M', [u'a\u010dka', u'a\u010dk'])] 
    """
    ATTR_VALUES_ALL   = None
    ATTR_VALUES_NO_NEO = None
    ATTR_VALUES_NO_NEO_COM = None
    ATTR_VALUES_NO_COM = None

    @classmethod
    def init_attr_values(cls):
        if cls.ATTR_VALUES_ALL:
            return
        cls.ATTR_VALUES_ALL = []
        cls.ATTR_VALUES_NO_NEO = []
        cls.ATTR_VALUES_NO_NEO_COM = []
        cls.ATTR_VALUES_NO_COM = []
        for comparation in base.ATTR_COMPARATION.values:
            #for type_ in base.ATTR_ADJ_TYPE.values:
            for num in base.ATTR_NUMBER.values:
                for decl in base.ATTR_DECLINATION.values:
                    for gender in base.ATTR_GENDER.values:
                        #yield comparation, type_, num, decl, gender
                        # type_, 
                        if comparation!="P_N":
                            cls.ATTR_VALUES_NO_NEO.append((comparation, num, decl, gender))
                        if comparation=="P_O":
                            cls.ATTR_VALUES_NO_NEO_COM.append((comparation, num, decl, gender))
                        if comparation.startswith("P_"):
                            cls.ATTR_VALUES_NO_COM.append((comparation, num, decl, gender))
                        cls.ATTR_VALUES_ALL.append((comparation, num, decl, gender))
        assert cls.ATTR_VALUES_ALL


    PARAM_NAME_LIST = ["apply_vc_a", ("has_neo", "n"), ("has_com", "c"), ("com_wp1_suff", "s")]

    def __init__(self, word_base, apply_vc_a=True, 
                 has_neo=True, has_com=True, 
                 com_wp1_suff=None, is_suffix=False, 
                 sri=None, status="T"):
        """
        NOTE: if ajdective.constructor changes default values - it must be changed down in wts adding too

        com_wp1_suff in ("ji", "iji", None -> will return both in exception)
        word_type is used just to override some circular deps stuff - ADJECTIVES -> Adjective -> ADJECTIVES
        """
        #attrs_ch=[base.ATTR_COMPARATION, base.ATTR_ADJ_TYPE, base.ATTR_NUMBER, 
        #          base.ATTR_DECLINATION, base.ATTR_GENDER])
        if not self.ATTR_VALUES_ALL:
            # TODO: check that this is called only once
            self.init_attr_values()

        if apply_vc_a is None: # TODO: not very nice ...
            self.suffname_p_n = "ADJ#P_N#-A"
            apply_vc_a = True
        else:
            if not apply_vc_a:
                self.suffname_p_n = "ADJ#P_N#-A"
            else:
                self.suffname_p_n = "ADJ#P_N"
            
        self.params_init = {"apply_vc_a"  : apply_vc_a, 
                            "has_neo"     : has_neo, 
                            "has_com"     : has_com, 
                            "com_wp1_suff": com_wp1_suff, 
                            }
        super(Adjective, self).__init__(word_type=ADJECTIVES, word_base=word_base, 
                                        attr_vals_fix=[], is_suffix=is_suffix, 
                                        status=status)
        self.sri = sri
        self.com_wp1_suff = com_wp1_suff
        self.has_neo, self.has_com = has_neo, has_com
        self.apply_vc_a = apply_vc_a
        self.is_base_suffix = (self.is_suffix and self.word_base=="")
        if self.has_neo:
            if self.has_com:
                self.attr_values = self.ATTR_VALUES_ALL
            else:
                self.attr_values = self.ATTR_VALUES_NO_COM
        else:
            if self.has_com:
                self.attr_values = self.ATTR_VALUES_NO_NEO
            else:
                self.attr_values = self.ATTR_VALUES_NO_NEO_COM
        # TODO: this fails for base suffixes: assert not(self.is_suffix and self.com_wp1_suff)
        #just a check
        #if self.apply_vc_a:
        #    self.word_lexem = _apply_vc_a(self.word_base)
        #else:
        #    self.word_lexem = self.word_base
        # if False:
        # #if self.is_suffix:
        #     wb, ws = split_by_last_AEIOU(self.word_lexem)
        #     self.word_lexem = wb
        #     self.wb_comp = self.word_lexem
        if self.is_base_suffix:
            self.wb_comp = self.word_lexem = ""
        else:
            base_last_char_when_AEIOU = split_by_last_AEIOU(self.word_base)[1]
            if self.has_neo:
                if base_last_char_when_AEIOU!="" :
                    raise BadParamsInitError("For %s base ends with AEIOU, so has_neo has to be False, but is True (%s)" % (
                                             repr(self.word_base), self.params_init))
            else:
                if base_last_char_when_AEIOU!="i":
                    raise BadParamsInitError("For %s base has has_neo=False, but it doesn't end with 'i' (%s)" % (
                                             repr(self.word_base), self.params_init))
            if self.apply_vc_a:
                self.word_base  = _remove_vc_a(self.word_base)
                self.word_lexem = _apply_vc_a(self.word_base)
                # TODO: in this case use $word_base0
            else:
                self.word_lexem = self.word_base

            self.word_base_changed = (self.word_base!=word_base)

            lexem_candidate, last_char_when_AEIOU = split_by_last_AEIOU(self.word_lexem)
            if last_char_when_AEIOU=="":
                self.wb_comp = self.word_base # TODO: = lexem or base?
            else:
                self.word_lexem = lexem_candidate # split_by_last_AEIOU(self.word_lexem)[0]
                self.wb_comp = self.word_lexem

    def _get_forms(self):       self._init_forms(); return self._forms
    def _get_forms_flat(self):  self._init_forms(); return self._forms_flat
    def _get_forms_stats(self): self._init_forms(); return self._forms_stats

    def _get_forms(self):       self._init_forms(); return self._forms
    def _get_forms_flat(self):  self._init_forms(); return self._forms_flat
    def _get_forms_stats(self): self._init_forms(); return self._forms_stats
    def _get_com_base(self):    self._init_forms(); return self._com_base
    def _get_com_base_ws(self): self._init_forms(); return self._com_base_ws
    def _get_com_lexem(self):   self._init_forms(); return self._com_lexem
    def _get_sup_base(self):    self._init_forms(); return self._sup_base
    def _get_sup_base_ws(self): self._init_forms(); return self._sup_base_ws
    def _get_sup_lexem(self):   self._init_forms(); return self._sup_lexem

    forms_flat  = property(_get_forms_flat )
    forms       = property(_get_forms      )
    forms_stats = property(_get_forms_stats)
    com_base    = property(_get_com_base   )
    com_base_ws = property(_get_com_base_ws)
    com_lexem   = property(_get_com_lexem  )
    sup_base    = property(_get_sup_base   )
    sup_base_ws = property(_get_sup_base_ws)
    sup_lexem   = property(_get_sup_lexem  )

    def _init_forms(self):
        if hasattr(self, "_forms"):
            return
        if self.has_com:
            self._com_base_ws = self.word_type.get_comp_base_suff(self.wb_comp, wp1_suff=self.com_wp1_suff, 
                                                                 is_suffix=self.is_suffix, apply_vc_a=self.apply_vc_a)
            if not isinstance(self._com_base_ws, (tuple, list)):
                raise Exception("%s hasn't got enough info for determining comparative word base. got: %s" % (
                                self, self._com_base_ws))
            self._com_base = "".join(self._com_base_ws)
            self._com_lexem = split_by_last_AEIOU(self._com_base)[0]

            self._sup_base_ws = self.word_type.get_supl_base_suff(self.wb_comp, com_wp1_suff=self.com_wp1_suff, 
                                                                 is_suffix=self.is_suffix, apply_vc_a=self.apply_vc_a)
            self._sup_base = "".join(self._sup_base_ws)
            self._sup_lexem = split_by_last_AEIOU(self._sup_base)[0]

        # TODO: optimize, suffixes should be calculated on class level
        if self.is_base_suffix:
            pass
        else:
            assert self.word_base and self.word_lexem 
        if self.has_com:
            assert self._com_base and self._sup_base
        self._forms = {}
        for comparation in base.ATTR_COMPARATION.values:
            if not self.has_neo and comparation=="P_N":
                continue
            if not self.has_com and not comparation.startswith("P_"):
                continue
            #for type_ in base.ATTR_ADJ_TYPE.values:
            if comparation in ("P_N","P_O"):
                word_base = self.word_base
                lexem = self.word_lexem
                if comparation=="P_N":
                    # TODO: use suffixes directly - suffixes_neo_no_a
                    assert self.suffname_p_n.startswith("ADJ#P_N")
                    suff = WORD_TYPE.get_suffixes(self.suffname_p_n)
                else:
                    suff = WORD_TYPE.get_suffixes("ADJ#P_O")
            else:
                suff = WORD_TYPE.get_suffixes("ADJ#P_O")
                if comparation=="COM":
                    word_base = self._com_base
                    lexem = self._com_lexem
                else:
                    assert comparation=="SUP", comparation
                    word_base = self._sup_base
                    lexem = self._sup_lexem
            if not self.is_base_suffix:
                assert suff and word_base
            sforms, swords = suff.get_forms(word_base, lexem)
            for k,v in sforms.iteritems():
                #key = "%s/%s/%s" % (comparation, type_, k)
                key = "%s/%s" % (comparation, k)
                assert key.count("/")==3, key
                #assert key.count("/")==4, key
                assert key not in self._forms
                self._forms[key]=v

        self.init_forms_common()

        # self.forms       = self._forms      
        # self.forms_flat  = self._forms_flat  
        # self.forms_stats = self._forms_stats

        if not self.is_base_suffix: 
            # wb=brutaln -> ff[0][1]=brutalni
            assert len(self.forms_flat[0][1])==1, self.forms_flat[0][1]
            if not self.word_base in self.forms_flat[0][1]:
                raise BadParamsInitError("For %s base got lexem %s, but base not same as first form (%s). Maybe params_init is bad, or some vc is missing? (params=%s)" % (
                                          repr(self.word_base), repr(self.word_lexem), 
                                          self.forms_flat[:2], self.params_init))
            # assert self.word_base in self.forms_flat[0][1]
            # self.word_base = self.forms_flat[0][1][0]
            # self.word_base_changed = True
            # raise Exception("For %s/%s first form %s is not equal to word_base (pi=%s)" % (
            #                  self.word_base, self.word_lexem, self.forms_flat[0], 
            #                  self.params_init))


# ---------------------------------------

class AdjectiveType(base.ChangeableWordType):
    COMP_BASE_EXCEPTIONS={u"dobar" : u"bolji", 
                          u"zao"   : u"gori",
                          u"malen" : u"manji",
                          u"velik" : u"veći",
                          u"dug"   : u"duži",  # TODO: also dulji
                          u"lak"   : u"lakši",
                          u"lijep" : u"ljepši",
                          u"krnj"  : u"krnji",
                          u"riđ"   : u"riđi",
                          u"vruć"  : u"vrući", # TODO: check vrućiji??
                          u"širok" : u"širi",
                          u"težak" : u"teži",
                          u"gorak" : u"gorči",
                          u"krepak": u"krepči", # TODO: krepkiji
                          }

    @classmethod
    def get_comp_base_suff(cls, word_base, wp1_suff=None, is_suffix=False, apply_vc_a=True):
        """
        TODO: make this normal object method in Adjective class

        Can be done like this too: unicode("riđ","utf-8")
        >>> [AdjectiveType.get_comp_base_suff(w) for w in ("dobar", "lak", "riđ")] 
        [(u'bolj', u'i'), (u'lak\u0161', u'i'), (u'ri\u0111', u'i')]

        TODO: book problem Debeliji -> deblji - see 241 d) 
        >>> [AdjectiveType.get_comp_base_suff(w) for w in ("veseo", "debeo", "pretio")] 
        [(u'vesel', u'iji'), (u'debel', u'iji'), (u'pretil', u'iji')]
        >>> [AdjectiveType.get_comp_base_suff(w) for w in ("lud", "blag", "gluh", 
        ...                                                "jak", "crn", "bijel", 
        ...                                                "čest", "krut", "brz", 
        ...                                                "grub", "tup", "kriv")]  # doctest: +NORMALIZE_WHITESPACE
        [(u'lu\u0111', u'i'), (u'bla\u017e', u'i'), (u'glu\u0161', u'i'), 
         (u'ja\u010d', u'i'), (u'crnj', u'i'), (u'bjelj', u'i'), 
         (u'\u010de\u0161\u0107', u'i'), (u'kru\u0107', u'i'), (u'br\u017e', u'i'), 
         (u'grublj', u'i'), (u'tuplj', u'i'), (u'krivlj', u'i')]

        >>> [AdjectiveType.get_comp_base_suff(w) for w in ("čvrst",)]
        [(u'\u010dvr\u0161\u0107', u'i')]

        For 1 word-parts word there are two versions but I don't know which is correct - so return both:
        This is ok: 
            [(u'bos', u'iji'), (u'plav', u'iji'), (u'prost', u'iji')]
        >>> [AdjectiveType.get_comp_base_suff(w) for w in ("bos", "plav", "prost")] # doctest: +NORMALIZE_WHITESPACE
        [{(u'bo\u0161', u'i'): 0.5, (u'bos', u'iji'): 0.5}, 
         {(u'plav', u'iji'): 0.5, (u'plavlj', u'i'): 0.5}, 
         {(u'prost', u'iji'): 0.5, (u'pro\u0161\u0107', u'i'): 0.5}]

        This is ok: 
            [(u'siv', u'iji'), (u'\u010dist', u'iji'), (u'zdrav', u'iji')]
        >>> [AdjectiveType.get_comp_base_suff(w) for w in ("siv", "čist", "zdrav")]  # doctest: +NORMALIZE_WHITESPACE
        [{(u'siv', u'iji'): 0.5, (u'sivlj', u'i'): 0.5}, 
         {(u'\u010di\u0161\u0107', u'i'): 0.5, (u'\u010dist', u'iji'): 0.5}, 
         {(u'zdravlj', u'i'): 0.5, (u'zdrav', u'iji'): 0.5}]

        But I can force which is correct - like this:
        >>> [AdjectiveType.get_comp_base_suff(w, wp1_suff="iji") for w in ("siv", "čist", "zdrav")]  # doctest: +NORMALIZE_WHITESPACE
        [(u'siv', u'iji'), (u'\u010dist', u'iji'), (u'zdrav', u'iji')]

        or force WRONG one :) like this:
        >>> [AdjectiveType.get_comp_base_suff(w, wp1_suff="ji") for w in ("siv", "čist", "zdrav")]  # doctest: +NORMALIZE_WHITESPACE
        [(u'sivlj', u'i'), (u'\u010di\u0161\u0107', u'i'), (u'zdravlj', u'i')]

        Nepostojano A - remove it from more than one word-parts (slogova)
        >>> AdjectiveType.get_comp_base_suff("bistar")
        (u'bistr', u'iji')
        >>> AdjectiveType.get_comp_base_suff("slastan")
        (u'slastn', u'iji')

        >>> AdjectiveType.get_comp_base_suff("zadovoljan")
        (u'zadovoljn', u'iji')

        with other vc-s
        >>> AdjectiveType.get_comp_base_suff("gibak")
        (u'gipk', u'iji')

        For 'lijen' is 1 wparts word - sometimes is ok ji and sometime iji - only one is correct. Function returns both:
        >>> [AdjectiveType.get_comp_base_suff(w) for w in ("krotak", "slavan", "lijen", "trijezan")] # doctest: +NORMALIZE_WHITESPACE
        [(u'krotk', u'iji'), (u'slavn', u'iji'), 
         {(u'ljenj', u'i'): 0.5, (u'ljen', u'iji'): 0.5}, 
         (u'trjezn', u'iji')]

        TODO: in book žarak->žarči->najžarči, but rules say different:
        >>> AdjectiveType.get_comp_base_suff("žarak") # doctest: +NORMALIZE_WHITESPACE
        (u'\u017eark', u'iji')
        """
        word_base = to_unicode(word_base)
        
        is_base_suffix = (is_suffix and word_base=="")
        if is_base_suffix:
            assert wp1_suff
            return "", wp1_suff

        #if wp1_suff:
        #    wp1_suff = to_unicode(wp1_suff)

        if word_base in cls.COMP_BASE_EXCEPTIONS: 
            # TODO: ignored for now since it is needed in detection
            #       assert not wp1_suff
            word_base_comp = cls.COMP_BASE_EXCEPTIONS[word_base] 
            base, suff = split_by_last_AEIOU(word_base_comp)
        else:
            word_base_comp = word_base
            if "ije" in word_base_comp:
                word_base_comp = word_base_comp.replace("ije", "je")
            if is_suffix:
                wparts = 100 # can indicate is_suffix
                if apply_vc_a:
                    if len(word_base_comp)==2 and word_base_comp[0]=="a":
                        word_base_comp = word_base_comp[1]
                    else:
                        word_base_comp = _apply_vc_a(word_base_comp)
            else:
                wparts = count_wparts(word_base_comp, check_len=False)
                # TODO: check if this is allways the case nepostojano A 
                if wparts>1: #and word_base_comp[-2]=="a" and word_base_comp[-1] not in AEIOU:
                    if apply_vc_a:
                        word_base_comp = _apply_vc_a(word_base_comp)
                    else:
                        word_base_comp = word_base_comp

            #TODO: in book žarak->žarči->najžarči, but rules say different:
            # NOTE: these words we have registred (book) that apply to ji rule
            if word_base in (u"lud", u"mlad", u"tvrd", u"blag", u"drag",
                             u"gluh", u"suh", u"jak", u"crn", u"bijel",
                             u"čest", u"čvrst", u"gust", u"krut", u"ljut", u"žut",
                             u"brz", u"grub", u"glup", u"tup", u"živ", u"kriv"):
                assert wparts==1, word_base_comp
                # TODO: ignored for now since it is needed in detection
                #       assert not wp1_suff
                # TODO: assert word_base_comp[-1] not in AEIOU
                base, suff = WordSuffixes.get_form("dummy", word_base_comp, "ji", join_wf=False)
            # TODO: book problem Debeliji -> deblji - see 241 d) - see above in doctest
            elif wparts==1:
                # NOTE: important - for 1 wparts words - sometimes is ok ji and sometime iji - only one is correct
                if wp1_suff:
                    assert wp1_suff in ("iji", "ji"), wp1_suff
                    base, suff = WordSuffixes.get_form("dummy", word_base_comp, wp1_suff, join_wf=False)
                else:
                    base1, suff1 = WordSuffixes.get_form("dummy", word_base_comp, "ji", join_wf=False)
                    base2, suff2 = WordSuffixes.get_form("dummy", word_base_comp, "iji", join_wf=False)
                    return {(base1, suff1) : 0.5, (base2, suff2) : 0.5}
            elif word_base_comp[-2:] in ("ak", "ek", "ok"): 
                # p. 122, t.241
                # TODO: ignored for now since it is needed in detection
                #       assert not wp1_suff
                word_base_comp = word_base_comp[:-2]
                if word_base_comp=="":
                    assert is_suffix
                    base, suff = "", "ji"
                else:
                    base, suff = WordSuffixes.get_form("dummy", word_base_comp, "ji", join_wf=False)
            else:
                # TODO: ignored for now since it is needed in detection
                #        assert not wp1_suff
                base, suff = WordSuffixes.get_form("dummy", word_base_comp, "iji", join_wf=False)
        if not (base[-1] not in AEIOU):
            raise BadParamsInitError("For %s base invalid last char in base %s" %
                                     (repr(word_base), repr(base),))
        return base, suff

    @classmethod
    def get_supl_base_suff(cls, word_base, com_wp1_suff=None, is_suffix=False, apply_vc_a=True):
        """
        TODO: make this object method in Adjectives
        veseo -> veseo+iji -> vesel+iji -> najveseliji
        >>> AdjectiveType.get_supl_base_suff("veseo")
        (u'najvesel', u'iji')

        >>> [AdjectiveType.get_supl_base_suff(w) for w in ("bijel", "dobar", "lak", "gibak", "dalek", "dug", 
        ...                                                "kratak", "plodan", "velik", "rijedak")] # doctest: +NORMALIZE_WHITESPACE
        [(u'najbjelj', u'i'), (u'najbolj', u'i'), (u'najlak\u0161', u'i'), 
         (u'najgipk', u'iji'), (u'najdalj', u'i'), (u'najdu\u017e', u'i'), 
         (u'najkratk', u'iji'), (u'najplodn', u'iji'), (u'najve\u0107', u'i'), 
         (u'najrjetk', u'iji')]

        """
        wb,ws = cls.get_comp_base_suff(word_base, wp1_suff=com_wp1_suff, 
                                       is_suffix=is_suffix, apply_vc_a=apply_vc_a)
        if is_suffix:
            base_supl = WordSuffixes.get_form("dummy", "naj$__lexem__$", wb)
        else:
            base_supl = WordSuffixes.get_form("dummy", "naj", wb)
        return base_supl, ws

    # @classmethod
    # def suggest_suffix(cls, word_base, word_base=None, is_suffix=False):
    #     raise Exception("can't be solved until COM/SUP is added and name4detection too")
    #     last_char = word_base[-1]
    #     if last_char=="i":
    #         return {"ODR": ""} 
    #     else:
    #         return {"NEO": ""} 
    
    # ------------- OBJECT METHODS ----------------

    def __init__(self):
        self._wts_forms_initialized = False
        super(AdjectiveType, self).__init__("ADJ", "Pridjevi", 
                                            attrs_ch=[base.ATTR_COMPARATION, # base.ATTR_ADJ_TYPE,
                                                      base.ATTR_NUMBER, base.ATTR_DECLINATION, 
                                                      base.ATTR_GENDER])
        """ NOTE: for adjectives normal is that VC A (nepostojano a) is applied. 
                  But here situation is opposite, we note each wts with param apply_vc_a=True, 
                  where it should be applied.
        """
        # oo", "opće opisno značenje
        # has_neo=True, has_com=True, com_wp1_suff=?
        # NOTE: for adjectives blank suffix not needed currently - can't find example at all
        #       self._add_wts({}, ""          ,  -1, "##", "", "")
        self._add_wts({}, "an"        ,   2, "oo", "", "brižan", apply_vc_a=True)
        self._add_wts({}, "an"        ,   2, "oo_2", "", "srčan")
        self._add_wts({}, "en"        ,   2, "oo", "", "božanstven")
        self._add_wts({}, "evan"      ,   1, "oo", "", "duševan", apply_vc_a=True)
        self._add_wts({}, "ovan"      ,   1, "oo", "", "masovan", apply_vc_a=True)
        self._add_wts({}, "ičan"      ,   1, "oo", "", "energičan", apply_vc_a=True)
        self._add_wts({}, "it"        ,   1, "oo", "", "čestit")
        self._add_wts({}, "nat"       ,   1, "oo", "", "lisnat")
        # TODO: prefiksalna tvorba 424/208 str.
        # sl", "sličnost
        self._add_wts({}, "ast"       ,   3, "sl", "", "sabljast")
        # ob", "obilje 
        self._add_wts({}, "av"        ,  -1, "ob", "", "bodljikav")
        self._add_wts({}, "at"        ,  -1, "ob", "", "glavat")
        self._add_wts({}, "iv"        ,   1, "ob", "", "pljesniv")
        self._add_wts({}, "ljiv"      ,   1, "ob", "", "crvljiv")
        self._add_wts({}, "ovit"      ,  -1, "ob", "", "brdovit")
        self._add_wts({}, "evit"      ,  -1, "ob", "", "grčevit")
        # TODO: prefikslno pre-", "str. 210
        # mg", "mogućnost
        self._add_wts({}, "iv"        ,  -1, "mg", "", "djeljiv")
        self._add_wts({}, "jiv"       ,  -1, "mg", "", "djeljiv")
        self._add_wts({}, "ljiv"      ,  -1, "mg", "", "djeljiv")
        self._add_wts({}, "av"        ,  -1, "mg", "", "brbljav")
        self._add_wts({}, "ak"        ,   0, "mg", "", "sklizak", apply_vc_a=True)
        # pj", "pojačani
        self._add_wts({}, "cat"       ,  -1, "pj", "", "bjelcat")
        self._add_wts({}, "ovetan"    ,  -1, "pj", "LIST:","bogovetan, ciglovetan, dugovetan, istovetan", apply_vc_a=True)
        # de", "pridjevne umanjenice
        self._add_wts({}, "kast"      ,  -1, "de", "", "bjelkast")
        self._add_wts({}, "ičast"     ,  -1, "de", "", "bjeličast")
        # TODO: prefiksalna tvorba
        # With this i have problem - so apply_vc_a is None - what mean - apply for lexem but use $word_base0
        self._add_wts({}, "ačak"      ,   0, "de", "LIST:", "ludačak, punačak, slabačak, suhačak", 
                                                   apply_vc_a=None)
        self._add_wts({}, "ahan"      ,   0, "de", "", "živahan", apply_vc_a=True)
        self._add_wts({}, "an"        ,   0, "de", "", "tihan")
        self._add_wts({}, "ašan"      ,   0, "de", "", "punašan", apply_vc_a=True)
        self._add_wts({}, "ešan"      ,   0, "de", "LIST:", "malešan, vremešan", apply_vc_a=True)
        self._add_wts({}, "jušan"     ,   0, "de", "", "majušan", apply_vc_a=True)
        self._add_wts({}, "uljast"    ,   0, "de", "", "duguljast")
        self._add_wts({}, "uljav"     ,   0, "de", "", "modruljav")
        self._add_wts({}, "unjav"     ,   0, "de", "", "bljedunjav")
        self._add_wts({}, "ušan"      ,   0, "de", "", "mekušan", apply_vc_a=True)
        self._add_wts({}, "uškast"    ,   0, "de", "LIST:", "ljepuškast, debeljuškast")
        # od", "odnosni
        # skupina 1
        # TODO: has_neo=True, has_com=True, com_wp1_suff=?
        self._add_wts({}, "ov"        ,   -1, "od1", "", "banov", has_neo=True, has_com=False)
        self._add_wts({}, "ev"        ,   -1, "od1", "", "pjevačev", has_neo=True, has_com=False)
        self._add_wts({}, "in"        ,   -1, "od1", "", "baničin", has_neo=True, has_com=False)
        # TODO: je li potrebno označiti skupine?? 
        # TODO: has_com=True can be in some cases, but generally not
        self._add_wts({}, "ski"       ,   -1, "od2", "", "klupski"      , has_neo=False, has_com=False)
        self._add_wts({}, "ovski"     ,   -1, "od2", "", "begovski"     , has_neo=False, has_com=False)
        self._add_wts({}, "evski"     ,   -1, "od2", "", "marševski"    , has_neo=False, has_com=False)
        self._add_wts({}, "inski"     ,   -1, "od2", "", "sestrinski"   , has_neo=False, has_com=False)
        self._add_wts({}, "ički"      ,   -1, "od2", "", "optimistički" , has_neo=False, has_com=False)
        self._add_wts({}, "ački"      ,   -1, "od2", "", "zagrebački"   , has_neo=False, has_com=False)
        self._add_wts({}, "anski"     ,   -1, "od2", "", "poštanski"    , has_neo=False, has_com=False)
        self._add_wts({}, "ni"        ,   -1, "od3", "", "baletni"      , has_neo=False, has_com=False)
        self._add_wts({}, "ani"       ,   -1, "od3", "", "brojčani"     , has_neo=False, has_com=False)
        self._add_wts({}, "eni"       ,   -1, "od3", "", "bedreni"      , has_neo=False, has_com=False)
        self._add_wts({}, "ovni"      ,   -1, "od3", "", "bankovni"     , has_neo=False, has_com=False)
        self._add_wts({}, "evni"      ,   -1, "od3", "", "bojevni"      , has_neo=False, has_com=False)
        # TODO: apply_vc_all is not used at all, and apply_vc_a could be subst and transfered back with vc_list="A"
        self._add_wts({}, "ji"        ,    2, "od4", "", "jelenji, pileći, ptičji, kozji", has_neo=False, 
                                         has_com=False, apply_vc_all=True) # note n+j->nj, tj->ć, c+j->č
        self._add_wts({}, "iji"       ,    0, "od4", "", "čovječiji"    , has_neo=False, has_com=False)
        self._add_wts({}, "ašnji"     ,   -1, "od5", "", "jučerašnji"   , has_neo=False, has_com=False)
        self._add_wts({}, "nji"       ,   -1, "od5", "", "današnji"     , has_neo=False, has_com=False)
        self._add_wts({}, "šnji"      ,   -1, "od5", "", "nekadašnji"   , has_neo=False, has_com=False)
        # TODO: strange - it makes problem if this is not unicode??
        self._add_wts({}, "aći"       ,   -1, "od6", "", u"brijaći"     , has_neo=False, has_com=False)
        self._add_wts({}, "eći"       ,   -1, "od6", "LIST:", "srneći"  , has_neo=False, has_com=False)

        # base suffixes
        for key, params_init in self.iter_param_combinations():
            self._add_wts({}, "$BASE$"       ,   -1, key, "", ""  , **params_init)

    def _add_wts(self, attrs_fix, suff_value, freq_type, group, 
                 *args, **kwargs):
        if kwargs.get("com_wp1_suff", ""):
            super(AdjectiveType, self)._add_wts(attrs_fix, suff_value, freq_type, group, 
                                                *args, **kwargs)
        else:
            # This must be define - so we add two suffixes
            kwargs["com_wp1_suff"]="ji"
            super(AdjectiveType, self)._add_wts(attrs_fix, suff_value, freq_type, group+"_ji", 
                                                *args, **kwargs)
            kwargs["com_wp1_suff"]="iji"
            super(AdjectiveType, self)._add_wts(attrs_fix, suff_value, freq_type, group+"_iji", 
                                                *args, **kwargs)

    # --------------------------------------------

    # TODO: I hope that I'll get rid of these suffix methods
    @classmethod
    def get_comparation_values(cls): 
        for comparation in base.ATTR_COMPARATION.values:
            yield comparation
    # def get_comparation_type_values(cls): 
    #     for comparation in base.ATTR_COMPARATION.values:
    #         for type in base.ATTR_ADJ_TYPE.values:
    #             yield comparation, type

    # --------------------------------------------

    def get_suffix_type_comparation_dict(self):
        """
        TODO: this code is copied and adjusted from nouns, so make it DRY
        """
        if not getattr(self, "suffix_type_comparation_dict", None):
            self.suffix_type_comparation_dict = {}
            for comparation in self.get_comparation_values():
                self.suffix_type_comparation_dict["%s" % (comparation)] = {}
            # for comparation, type in self.get_comparation_type_values():
            #     self.suffix_type_comparation_dict["%s/%s" % (comparation, type)] = {}

            for name4detect, suffixes in self.suffixes4detection.iteritems():
                # TODO: i know i know, not nice, but i have deadlines ;)
                # NOTE: from suffixes.name = 'ADJ#P_O#' -> get P_O as Positive and Odredjeni
                type_comparation, suf_id = name4detect.split("#")
                assert type_comparation== suffixes.name.split("#")[1]
                if type_comparation not in self.suffix_type_comparation_dict:
                    raise Exception("Adjectives: %s not in %s (name=%s)" % (type_comparation, self.suffix_type_comparation_dict.keys(), name4detect))
                assert suf_id not in self.suffix_type_comparation_dict[type_comparation]
                self.suffix_type_comparation_dict[type_comparation][suf_id] = suffixes
        return self.suffix_type_comparation_dict

    # --------------------------------------------

    def iter_suffix_cross_table(self):
        """ returns 
        M - suf1 : S/N S/G ... S/I  | P/N ... P/I
        >>> l = [(iter2.comparation, iter2.suf_id, iter2.suffix.name) for iter2 in ADJECTIVES.iter_suffix_cross_table()]

        TODO: maybe P_N#-A shouldn't be listed?
        >>> len(l)
        9
        >>> l[0]
        ('P_N', '-', u'ADJ#P_N#')
        >>> l[-1]
        ('P_O', '-', u'ADJ#P_O#')
        """
        suffix_dict = self.get_suffix_type_comparation_dict()
        for comparation in self.get_comparation_values():
        #for comparation, type in self.get_comparation_type_values():
            suffix_list = self.suffix_type_comparation_dict["%s" % (comparation)]
            suf_id_list = sorted(suffix_list.keys())
            for suf_id in suf_id_list:
                suffix = suffix_list[suf_id]
                for gender in base.ATTR_GENDER.values:
                    yield IterAttrs(self, suffix, suf_id=suf_id, add_gender=True,
                                      iter_attrs=[base.ATTR_NUMBER, base.ATTR_DECLINATION],
                                      gender=gender, comparation=comparation)
                                      #gender=gender, comparation=comparation, type=type)

    # --------------------------------------------

    def init_wts_forms(self):
        """ NOTE: This is slow ... not called initially
        """
        if self._wts_forms_initialized:
            return

        for code, wts in self.wts_list.iteritems():
            wts_forms = []
            # NOTE: if ajdective.constructor changes default values - it must be changed here too
            apply_vc_a = getattr(wts, "apply_vc_a", False)
            has_com = getattr(wts, "has_com", True)
            has_neo = getattr(wts, "has_neo", True)
            com_wp1_suff = getattr(wts, "com_wp1_suff", None)
            # TODO: check for each suffix that examples are ok: 
            #       e.g. check "ak" -> "k" but maybe base should be "" ("ak" rule - get ak away)
            # TODO: generate this only for not LIST: - for LIST: don't use suffix but word and mark it like this
            # TODO: pass parameter has_com, has_neo, wp1_ to Adjective() constructor
            if apply_vc_a and wts.suff_value.count("a")==1 and wts.suff_value.startswith("a"):
                # TODO: iterate for all possible not AEIOU and vocal changes?
                # NOTE: is there any case like "ank" - len is 3
                assert len(wts.suff_value)==2
            if wts.desc=="LIST:":
                word_base_list = wts.examples
                status="F" # confirmed - predef word_obj
            else:
                word_base_list = [wts.suff_value]
                status="T" # unconfirmed - suff word_obj
            for word_base in word_base_list:
                adjective = Adjective(wts.suff_value, 
                                      is_suffix = True if status=="T" else False,
                                      status=status,
                                      apply_vc_a=apply_vc_a, has_com=has_com, 
                                      has_neo=has_neo, 
                                      com_wp1_suff=com_wp1_suff)
                for key, form_list in adjective:
                    for ordnr, form in enumerate(form_list):
                        #                 word_obj , suff_key, suff_value))
                        wts_forms.append((adjective, key, ordnr+1, form))
            # NOTE: this call adds list of wts entries into suff.registry
            wts.add_forms(wts_forms) 
        self._wts_forms_initialized = True
        return


    @classmethod
    def iter_param_combinations(cls):
        """
        >>> sorted(list(AdjectiveType.iter_param_combinations())[:5]) # doctest: +NORMALIZE_WHITESPACE
        [('+A/+N/+C/ijiS', {'has_neo': True, 'com_wp1_suff': 'iji', 'apply_vc_a': True, 'has_com': True}), 
         ('+A/+N/+C/jiS', {'has_neo': True, 'com_wp1_suff': 'ji', 'apply_vc_a': True, 'has_com': True}), 
         ('+A/+N/-C/ijiS', {'has_neo': True, 'com_wp1_suff': 'iji', 'apply_vc_a': True, 'has_com': False}), 
         ('+A/+N/-C/jiS', {'has_neo': True, 'com_wp1_suff': 'ji', 'apply_vc_a': True, 'has_com': False}), 
         ('+A/-N/+C/jiS', {'has_neo': False, 'com_wp1_suff': 'ji', 'apply_vc_a': True, 'has_com': True})]
        """
        for apply_vc_a in (True, False):
            for has_neo in (True, False):
                for has_com in (True, False):
                    for com_wp1_suff in ("ji", "iji"): #, None):
                        params_init = {"apply_vc_a" : apply_vc_a, 
                                       "has_neo" : has_neo, 
                                       "has_com" : has_com, 
                                       "com_wp1_suff" : com_wp1_suff
                                      }
                        key = Adjective.params2key(params_init)
                        yield key, params_init 

# --------------------------------------------

if not base.is_word_type_registred("ADJ"):
    ADJECTIVES    = AdjectiveType()

    # TODO: adj_type_comparation
    WORD_TYPE = ADJECTIVES

    # ------------------- suffixes for pozitiv - određeni / neodređeni ----------------

    # neodređeni oblik
    # TODO: testiraj nepostojano a u SMN za dobar, kratak, sitan, topao, šupalj, radostan, zahvalan (str 63)
    # TODO: before 1st was %A0, then $word_base0
    suffixes_neo = WORD_TYPE.add_suffixes("P_N", "MANY", "", "P_N#-",
                           (base.ATTR_NUMBER, base.ATTR_DECLINATION, base.ATTR_GENDER),
                        """##   SINGULAR
                           ##   M                  F       N
                           ##   ----------------   ------- ---------------------
                           #N   %A0                a       o
                           #G   a                  e       a
                           #D   u                  oj      u
                           #A   a|0                u       o
                           #V   -                  -       -
                           #L   u                  oj      u
                           #I   im                 om      im

                           ##   PLURAL
                           #N   i                  e       a
                           #G   ih                 ih      ih
                           #D   im|ima             im|ima  im|ima
                           #A   e                  e       a
                           #V   -                  -       -
                           #L   im|ima             im|ima  im|ima
                           #I   im|ima             im|ima  im|ima
                        """)

    # TODO: MAYBE it should be done with word_type.add
    suffixes_neo_no_a = WORD_TYPE.add_suffixes("P_N#-A", "MANY", "", "P_N#-A",
                             suffixes_force= suffixes_neo.copy(name="ADJ#__dummy__",
                                          exceptions = {"S/N/M" : ["$word_base0"]}))
    # određeni oblik
    suffixes_odr = WORD_TYPE.add_suffixes("P_O", "MANY", "", "P_O#-",
                           (base.ATTR_NUMBER, base.ATTR_DECLINATION, base.ATTR_GENDER),
                        """##   SINGULAR
                           ##   M                  F       N
                           ##   ----------------   ------- ---------------------
                           #N   i                  a       o
                           #G   oga|og             e       oga|og
                           #D   omu|om             oj      omu|om
                           #A   oga|og             u       o
                           #V   i                  a       o
                           #L   om|ome             oj      om|ome
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

    # union of them - used in zamjenice pokazne
    #import copy
    #suffixes_bef = WORD_TYPE.get_suffixes("ADJ#P_N").suffixes.copy()

    WORD_TYPE.add_suffixes("P_N+O", "SOME", "", "",
                           suffixes_force=suffixes_neo.union(name="ADJ#__dummy__", 
                                                    suffixes_obj_other=suffixes_odr))
    #assert suffixes_bef==WORD_TYPE.get_suffixes("ADJ#P_N").suffixes
    #assert suffixes_bef!=WORD_TYPE.get_suffixes("ADJ#P_N+O").suffixes

    # TODO: not possible now: print s.pp_forms2(forms, (base.ATTR_GENDER, base.ATTR_NUMBER, base.ATTR_DECLINATION, ))
    # print_forms("P_O", "crven")

# ----------------------------------------------------------
else:
# ----------------------------------------------------------
    ADJECTIVES = base.get_word_type("ADJ")
    WORD_TYPE = ADJECTIVES

def test():
    print "%s: running doctests" % __name__
    import doctest
    doctest.testmod()
    base.run_doctests( ("test_adj.txt", "test_adj_wts.txt"))

if __name__ == "__main__":
    test()

