# coding=utf-8
#...    print "%-40s " % val, # doctest: +NORMALIZE_WHITESPACE
"""
# TODO: THIS IS SLOW - enable this later

>>> from datetime import datetime, timedelta
>>> started = datetime.now()
>>> WORD_TYPE.init_wts_forms()
>>> ended = datetime.now()

Currently this takes about 0.5 sec on my machine
>>> (ended - started) < timedelta(seconds=2)
True

#>>> from morphs import get_suff_registry
#>>> print get_suff_registry()
# from nouns: SR(1388 suffixes, 5123 SRI objects)
# from tests: SR(2922 suffixes, 26079 SRI objects)
"""
import logging

import base

from morphs import WordSuffixes, WordTypeSuffix, AEIOU, ChangeableWordBase, BadParamsInitError
from morphs import count_wparts, _remove_vc_a, _apply_vc_a, split_by_last_AEIOU

from text_hr.utils import iter_mine, to_unicode, init_logging, IterAttrs, iter_number_decl 


# ================================================================================ 
class Noun(ChangeableWordBase):
# ================================================================================ 
    """
    >>> def print_it(params_init):
    ...     key = Noun.params2key(params_init)
    ...     print repr(key), repr(Noun.key2params(key))

    >>> print_it({"apply_vc_a" : True, "gender" : None, "ext" : "", "spec" : ""})
    '$D/+A/$G/#E/#S' {'decl': None, 'gender': None, 'ext': '', 'apply_vc_a': True, 'spec': ''}

    >>> print_it({"apply_vc_a" : True, "gender" : None, "ext" : "ov", "spec" : None})
    '$D/+A/$G/ovE/$S' {'decl': None, 'gender': None, 'ext': 'ov', 'apply_vc_a': True, 'spec': None}

    >>> print_it({"apply_vc_a" : True, "gender" : "M", "ext" : "", "spec" : "0"})
    '$D/+A/MG/#E/0S' {'decl': None, 'gender': 'M', 'ext': '', 'apply_vc_a': True, 'spec': '0'}

    >>> print_it({"apply_vc_a" : True, "gender" : "N", "ext" : "ev", "spec" : "00"})
    '$D/+A/NG/evE/00S' {'decl': None, 'gender': 'N', 'ext': 'ev', 'apply_vc_a': True, 'spec': '00'}

    >>> print_it({"decl" : "I-F", "apply_vc_a" : True, "gender" : "F", "ext" : "ev", "spec" : "00"})
    'I-FD/+A/FG/evE/00S' {'decl': 'I-F', 'gender': 'F', 'ext': 'ev', 'apply_vc_a': True, 'spec': '00'}

    >>> print_it({"decl" : "I", "apply_vc_a" : True, "gender" : "F", "ext" : "ev", "spec" : "00"})
    'ID/+A/FG/evE/00S' {'decl': 'I', 'gender': 'F', 'ext': 'ev', 'apply_vc_a': True, 'spec': '00'}

    # TODO: enable this too
    # >>> auto = Noun("auto", "M", ext="", si="$WORD_BASEm")
    # >>> auto = Noun("auto", "M", ext="", si="om")
    # >>> auto = Noun("auto", "M", ext="", si="0")
    # >>> auto = Noun("auto", "M", ext="", si=0)

    >>> auto = Noun("auto", "M", ext="", spec="0")

    >>> auto.params_key, auto.params_key
    ('A-MoeD/+A/MG/#E/0S', 'A-MoeD/+A/MG/#E/0S')

    >>> auto.forms["S/N"]
    [u'auto']

    >>> auto.forms["S/G"]
    [u'auta']
    >>> auto.forms["P/I"]
    [u'autima']
    >>> auto[10]
    ('P/A', [u'aute'])
    >>> auto.forms_flat[0], auto.forms_flat[-1]
    (('S/N', [u'auto']), ('P/I', [u'autima']))


    >>> hrvoje = Noun("hrvoje", "M", ext="", spec="0")
    Traceback (most recent call last):
    ...
    BadParamsInitError: For gender M - attr_detected is 0 but detected that attr_detected should be 2 (hrvoje)

    # >>> hrvoje = Noun("hrvoje", "M", ext="")
    # For gender M - attr_detected is  and detected is attr_detected is same  (hrvoje), so inp. not needed anyway.

    >>> hrvoje = Noun("hrvoje", "M")
    >>> hrvoje.forms_flat[0], hrvoje.forms_flat[1], hrvoje.forms_flat[-1]
    (('S/N', [u'hrvoje']), ('S/G', [u'hrvoja']), ('P/I', [u'hrvojima']))
    >>> hrvoje.forms["P/N"]
    [u'hrvoji']

    #>>> print "TODO: str. 104, točka 197"

    The least specific case - the most general result:
    >>> ugao = Noun("ugao", "M")
    >>> ugao.forms_flat # doctest: +NORMALIZE_WHITESPACE
    [('S/N', [u'ugao']), ('S/G', [u'ugla']), ('S/D', [u'uglu']), 
     ('S/A', [u'ugla', u'ugao']), ('S/V', [u'ugao']), 
     ('S/L', [u'uglu']), ('S/I', [u'ugaom', u'uglom', u'uglem']), 
     ('P/N', [u'ugli', u'uglovi', u'uglevi']), 
     ('P/G', [u'ugla', u'uglova', u'ugleva']), 
     ('P/D', [u'uglima', u'uglovima', u'uglevima']), 
     ('P/A', [u'ugle', u'uglove', u'ugleve']), 
     ('P/V', [u'ugli', u'uglovi', u'uglevi']), 
     ('P/L', [u'uglima', u'uglovima', u'uglevima']), 
     ('P/I', [u'uglima', u'uglovima', u'uglevima'])]

    TODO: ...
    More specific case - a little less general result:
    # >>> ugao = Noun("ugao", "M", ext="ov") -> N##A-Moe/ov/*
    # >>> ugao.forms_flat
    # >>> ugao = Noun("ugao", "M", spec="1")
    # >>> ugao.forms_flat

    Specific result - precise result:
    >>> ugao = Noun("ugao", "M", ext="ov", spec="1")
    >>> ugao.forms_flat # doctest: +NORMALIZE_WHITESPACE
    [('S/N', [u'ugao']), ('S/G', [u'ugla']), ('S/D', [u'uglu']), 
     ('S/A', [u'ugla', u'ugao']), ('S/V', [u'ugao']), 
     ('S/L', [u'uglu']), ('S/I', [u'uglom']), 
     ('P/N', [u'uglovi']), ('P/G', [u'uglova']), ('P/D', [u'uglovima']), 
     ('P/A', [u'uglove']), ('P/V', [u'uglovi']), 
     ('P/L', [u'uglovima']), ('P/I', [u'uglovima'])] 

    # TODO: 
    # >>> parket = Noun("parket", "M", ext="") -> N##A-M0//*

    >>> parket = Noun("parket", "M", ext="", spec="0")
    >>> print parket
    W(u'parket'=N)
    >>> parket.forms_flat # doctest: +NORMALIZE_WHITESPACE
    [('S/N', [u'parket']), ('S/G', [u'parketa']), ('S/D', [u'parketu']), 
    ('S/A', [u'parketa', u'parket']), ('S/V', [u'parkete', u'parketu']), 
    ('S/L', [u'parketu']), ('S/I', [u'parketom', u'parketem']), 
    ('P/N', [u'parketi']), ('P/G', [u'parketa']), ('P/D', [u'parketima']), 
    ('P/A', [u'parkete']), ('P/V', [u'parketi']), 
    ('P/L', [u'parketima']), ('P/I', [u'parketima'])]

    # TODO: check all ok
    >>> Noun("poni", "M").forms_flat # doctest: +NORMALIZE_WHITESPACE
    [('S/N', [u'poni']), ('S/G', [u'ponija']), ('S/D', [u'poniju']), 
     ('S/A', [u'ponija', u'poni']), ('S/V', [u'poni']),
     ('S/L', [u'poniju']), ('S/I', [u'ponijem']), 
     ('P/N', [u'poniji']), ('P/G', [u'ponija']), ('P/D', [u'ponijima']), 
     ('P/A', [u'ponije']), ('P/V', [u'poniji']), 
     ('P/L', [u'ponijima']), ('P/I', [u'ponijima'])]

    NOTE: S/D+L should be gnu->gnuu
    >>> Noun("gnu", "M").forms_flat # doctest: +NORMALIZE_WHITESPACE
    [('S/N', [u'gnu']), ('S/G', [u'gnua']), ('S/D', [u'gnu']), 
     ('S/A', [u'gnua', u'gnu']), ('S/V', [u'gnu']), 
     ('S/L', [u'gnu']), ('S/I', [u'gnuom']), 
     ('P/N', [u'gnui']), ('P/G', [u'gnua']), ('P/D', [u'gnuima']), 
     ('P/A', [u'gnue']), ('P/V', [u'gnui']), 
     ('P/L', [u'gnuima']), ('P/I', [u'gnuima'])]

    >>> radio = Noun("radio", "M")
    >>> radio.forms_flat # doctest: +NORMALIZE_WHITESPACE
    [('S/N', [u'radio']), ('S/G', [u'radija']), ('S/D', [u'radiju']), 
    ('S/A', [u'radija', u'radio']), ('S/V', [u'radio']), 
    ('S/L', [u'radiju']), ('S/I', [u'radiom']), 
    ('P/N', [u'radiji']), ('P/G', [u'radija']), ('P/D', [u'radijima']), 
    ('P/A', [u'radije']), ('P/V', [u'radiji']), 
    ('P/L', [u'radijima']), ('P/I', [u'radijima'])]

    # >>> radio = Noun("radio", "M", ext="", spec="0")
    # >>> radio.forms["S/G"]
    # [u'radija']
    # >>> radio.forms["P/L"]
    # [u'radijima']

    >>> auto.forms["S/I"], radio.forms["S/I"], hrvoje.forms["S/I"]
    ([u'autom'], [u'radiom'], [u'hrvojem'])



    >>> print Noun("jelen", "M")._get_suffix()
    N##A-M0/*/*(Broj/Padez (deklinacija), 14 suffixes, based_on=)

    >>> print Noun("auto", "M")._get_suffix()
    N##A-Moe/*/*(Broj/Padez (deklinacija), 14 suffixes, based_on=)

    >>> print Noun("auto", "M", ext="", spec="0")._get_suffix()
    N##A-Moe//0(Broj/Padez (deklinacija), 14 suffixes, based_on=)

    >>> print Noun("ero", "M")._get_suffix()
    N##A-Moe/*/*(Broj/Padez (deklinacija), 14 suffixes, based_on=)

    >>> print Noun("poni", "M")._get_suffix()
    N##A-Moe//2(Broj/Padez (deklinacija), 14 suffixes, based_on=)

    >>> print Noun("gnu", "M")._get_suffix()
    N##A-Moe//1(Broj/Padez (deklinacija), 14 suffixes, based_on=)

    # Female
    # >>> print Noun("sestra", "F")._get_suffix()
    # ['F#E1', 'F#E2', 'F#E3', 'F#E4', 'F#E5', 'F#E6']

    # >>> print Noun("radost", "F")._get_suffix()
    # ['F#I1', 'F#I2', 'F#I3']

    # Neutral
    # >>> print Noun("pleme", "N")._get_suffix()
    # ['N#AE1', 'N#AE2', 'N#AE3', 'N#AE4']

    # >>> print Noun("rebro", "N")._get_suffix()
    # ['N#AE1', 'N#AE2', 'N#AE3', 'N#AE4']

    # >>> print Noun("radost", "N")._get_suffix()
    # Traceback (most recent call last):
    #     ...
    #     assert last_char in "oe", word_base
    # AssertionError: radost
    """
    ATTR_VALUES = None
    @classmethod
    def init_attr_values(cls):
        cls.ATTR_VALUES = []
        for num in base.ATTR_NUMBER.values:
            for decl in base.ATTR_DECLINATION.values:
                cls.ATTR_VALUES.append((num, decl))
        assert cls.ATTR_VALUES



    PARAM_NAME_LIST = ["decl", "apply_vc_a", "gender", "ext", "spec"]

    def __init__(self, word_base, gender=None,  
                 apply_vc_a=True, spec=None, ext=None,
                 is_suffix=False, sri=None, decl=None,
                 status="T"):
        """
        NOTE: if NOUNS.constructor changes default values - it must be changed down in wts adding too
        gender=None - autodetect
        """
        from nouns import NOUNS  # found no better way :(

        # attrs_fix=[base.ATTR_GENDER],
        # attrs_ch =[base.ATTR_NUMBER, 
        #            base.ATTR_DECLINATION])
        if not self.ATTR_VALUES:
            self.init_attr_values()
        self.attr_values = self.ATTR_VALUES

        self.gender = gender
        self.apply_vc_a = apply_vc_a
        self.ext, self.spec = ext, spec
        self.decl = decl
        if self.decl:
            assert self.decl in dict(NOUNS.get_params_add_for_gender(gender))

        self.is_suffix = is_suffix
        self.sri = sri
        self.params_init = { "gender"  : self.gender, 
                           }
        # NOTE: self.params_init["decl"] is set after
        self._suffix = None
        word_base = to_unicode(word_base)
        self.is_base_suffix = (self.is_suffix and word_base=="")

        # if word_base=="ugao":
        #     import pdb;pdb.set_trace() 
        # TODO: maybe not the best place for this - should be done once

        # TODO: not in function currently
        # for decl, attr_dict in self.PARAMS_ADD.iteritems():
        #     for attr in attr_dict.keys():
        #         if attr not in params_all:
        #             params_all.append(attr)
        # params_all = []
        # for attr in ["spec", "ext"]:
        #     if attr not in params_all:
        #         params_all.append(attr)
        # for attrname in params_all:
        #     if attrname in kwargs:
        #         val = kwargs.pop(attrname)
        #         self.params_init[attrname]=val
        #     else:
        #         val = None
        #     assert not hasattr(self, attrname), attrname
        #     setattr(self, attrname, val)
        # assert not kwargs, "unexpected args: %s" % kwargs
        # self.base_ext, base_ext="", to_unicode(base_ext), 
        # "base_ext" : base_ext,
        super(Noun, self).__init__(word_type=NOUNS, word_base=word_base, 
                                   attr_vals_fix=[gender], is_suffix=is_suffix,
                                   accept_attr_none=True, status=status)

        # TODO: this is copied from adj. - make it DRY?
        # if word_base=="radio" and self.gender is None:
        #     import pdb;pdb.set_trace() 
        if self.is_base_suffix:
            self.word_lexem = ""
            params_add_gender = NOUNS.get_params_add_for_gender(gender)
            assert len(params_add_gender)>0
            decl_names = [k for k,v in params_add_gender]
            if len(params_add_gender)==1:
                decl = params_add_gender[0][0]
                if self.decl:
                    if self.decl==decl:
                        pass
                        # logging.warning("base_suffix: decl %s defined and autodected same %s (%s)" % (self.decl, decl, self.word_base))
                    else:
                        raise BadParamsInitError("Base suffix decl passed %s and it should be %s (%s)" % 
                                                 (self.decl, decl, self.gender))
                self.decl = decl
            else:
                if not self.decl:
                    raise BadParamsInitError("Base suffix decl not passed and it should be one of the following %s (%s)" % 
                                             (decl_names, self.gender))
                assert self.decl in decl_names
        else:
            if self.apply_vc_a:
                self.word_base  = _remove_vc_a(self.word_base)
                self.word_lexem = _apply_vc_a(self.word_base)
                # TODO: in this case use $word_base0
            else:
                self.word_lexem = self.word_base
            self.word_base_changed = (self.word_base!=word_base)
            lexem_candidate, last_char_when_AEIOU = split_by_last_AEIOU(self.word_lexem)
            if last_char_when_AEIOU=="":
                pass
            else:
                # TODO: it seems that it works better without this
                # or self.word_base[-2:] in ("io",)
                if (last_char_when_AEIOU in ("i", "u")):
                    if self.gender is None:
                        self.gender="M" # first gender autodetect
                    assert self.gender=="M", self.gender
                    self.word_lexem = self.word_base
                else:
                    self.word_lexem = lexem_candidate # split_by_last_AEIOU(self.word_lexem)[0]

        suffix = self._get_suffix()
        self.params_init["decl"      ]=self.decl
        self.params_init["apply_vc_a"]=self.apply_vc_a
        self.params_init["ext"       ]=self.ext 
        self.params_init["spec"      ]=self.spec 

        # must be called by first forms_flat access 
        # self._init_forms()

    def _get_forms(self):       self._init_forms(); return self._forms
    def _get_forms_flat(self):  self._init_forms(); return self._forms_flat
    def _get_forms_stats(self): self._init_forms(); return self._forms_stats

    forms_flat  = property(_get_forms_flat  )
    forms       = property(_get_forms       )
    forms_stats = property(_get_forms_stats )

    def _get_suffix(self):
        if self._suffix:
            return self._suffix

        if self.is_base_suffix:
            assert self.decl
            ext = self.ext
            if ext is None:
                ext = "*"
            spec = self.spec
            if spec is None:
                spec = "*"
            self.suffname  = "N##%s/%s/%s" % (self.decl, ext, spec)
            self._suffix = WORD_TYPE.get_suffixes(self.suffname)
            return self._suffix

        # TODO: if self.is_base_suffix:
        suff_candidates = []
        last_char = self.word_base[-1]
        ext = None
        spec = None
        # TODO: use self.apply_vc_a
        if self.gender is None:
            # second gender autodetect
            assert not (last_char in ("i", "u")), "should have been autodetected before"

            if not last_char in AEIOU:
                raise BadParamsInitError("Gender autodetect failed - based on last char '%s' M/F can be (%s)" % 
                                         (last_char, self.word_base))
            else:
                if last_char in "a":
                    self.gender = "F"
                elif self.word_base[-2:]=="je":
                    self.gender = "M"
                elif last_char in "a":
                    self.gender = "F"
                elif self.word_base[-2:] in ("io","go","ko"):
                    # TODO: probably in these cases ext/spec can be defined too
                    self.gender = "M"
                else:
                    assert last_char in "oe"
                    raise BadParamsInitError("Gender autodetect failed - based on last char '%s' N/M can be (%s)" % 
                                             (last_char, self.word_base))
                
        if self.gender=="M":
            # TODO: if male what with ends with R?
            # TODO: later we need to have statistics (later) to define more precisely which suff to use
            if not last_char in AEIOU:
                self.decl = "A-M0"
            else:
                self.decl = "A-Moe"
                if last_char in "i":
                    ext, spec= "", "2"
                elif last_char in "u":
                    ext, spec= "", "1"
                elif self.word_base[-2:] in ("go","ko"):
                    ext, spec= "", "1"
                elif self.word_base[-2:]=="io":
                    ext, spec= "", "1"
                elif self.word_base[-2:]=="je":
                    ext, spec = "", "2"
                # TODO: when to use/detect this one?
                # suff_candidates.append("EA") # lower probability
        elif self.gender=="F":
            if last_char in "a":
                self.decl = "E-F"
            else:
                self.decl = "I-F"
        else:
            assert self.gender=="N", self.gender
            if not last_char in "oe":
                raise BadParamsInitError("For gender N - unexpected last char '%s' (%s)" % 
                                         (last_char, self.word_base))
            self.decl = "A-N"

        assert self.decl[self.decl.find("-")+1]==self.gender, "%s!=%s" % (self.decl, self.gender)

        for attr in ("ext", "spec"):
            if attr=="ext":
                attr_detected = ext
                attr_obj = self.ext
            else:
                assert attr=="spec"
                attr_detected = spec
                attr_obj = self.spec

            if attr_obj is not None:
                if attr_obj==attr_detected:
                    # TODO: use logging.warning - this is with print because of testing. find a way ...
                    logging.info("%s - For gender %s - attr_detected is %s and detected is attr_detected is same %s (%s), so inp. not needed anyway." % 
                                 (self, self.gender, attr_obj, attr_detected, self.word_base))
                elif attr_detected!=None and attr_obj!=attr_detected:
                    raise BadParamsInitError("For gender %s - attr_detected is %s but detected that attr_detected should be %s (%s)" % 
                                             (self.gender, attr_obj, attr_detected, self.word_base))
            else:
                if attr_detected is None:
                    val = "*"
                else:
                    val = attr_detected
                setattr(self, attr, val)
        self.suffname  = "N##%s/%s/%s" % (self.decl, self.ext, self.spec)
        self._suffix = WORD_TYPE.get_suffixes(self.suffname)
        # A-M0//0 M#A01 N##A-M0//0(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        return self._suffix
        
    def _init_forms(self):
        if hasattr(self, "_forms"):
            return
        # TODO: optimize, suffixes should be calculated on class level
        # TODO: str 104/105 when it is applied - list of words, when sibilarization is not done, etc.
        if not self.is_base_suffix:
            if self.is_suffix:
                assert self.word_base
            else:
                assert self.word_base and self.word_lexem 
        suffix = self._get_suffix()

        self._forms = {}
        # if not self.is_base_suffix:
        #     assert suff and word_base
        sforms, swords = suffix.get_forms(self.word_base, self.word_lexem)
        for k,v in sforms.iteritems():
            #key = "%s/%s/%s" % (comparation, type_, k)
            key = k
            assert key.count("/")==1, key
            assert key not in self._forms
            self._forms[key]=v

        self.init_forms_common()

        if not self.is_base_suffix: 
            assert len(self._forms_flat[0][1])==1, self._forms_flat[0][1]
            if not self.word_base in self._forms_flat[0][1]:
                raise BadParamsInitError("For %s base got lexem %s, but base not same as first form (%s). Maybe params_init is bad, or some vc is missing? (params=%s)" % (
                                          repr(self.word_base), repr(self.word_lexem), 
                                          self._forms_flat[:2], self.params_init))

# ================================================================================ 
class NounType(base.ChangeableWordType):
# ================================================================================ 

    def __init__(self):
        super(NounType, self).__init__("N", "Imenice",
                                       attrs_fix=[base.ATTR_GENDER],  # , base.ATTR_N_SUFF
                                       attrs_ch=[base.ATTR_NUMBER, 
                                                 base.ATTR_DECLINATION])

        self.__init_suffixes()
        self.__init_wts()

    def get_params_add_for_gender(self, gender):
        ret = []
        for decl, vals in self.PARAMS_ADD.iteritems():
            # TODO: make this dry
            if decl[decl.find("-")+1]!=gender:
                continue
            ret.append((decl, vals))
        return ret

    def __init_suffixes(self):
        self._SUFFIX_TEMPL["A-M0"] = """  ##   SINGULAR
                               ##   M
                               ##   ----------
                               #N   $word_base0
                               #G   a
                               #D   u
                               ## NOTE: live / not live
                               #A   a|$word_base0
                               ## NOTE: single or both # TODO: this should be solved with exceptions
                               #V   %%Pe|u
                               #L   u
                               ## NOTE: single or both # TODO: this should be solved with exceptions
                               #I   om|em

                               ##   PLURAL
                               #N   %%S%(ext)si
                               #G   %(pg)s
                               #D   %%S%(ext)sima
                               #A   %(ext)se
                               #V   %%S%(ext)si
                               #L   %%S%(ext)sima
                               #I   %%S%(ext)sima
                               """
        #                              0                 1       2           3
        self.PARAMS_ADD["A-M0"] = {"ext" : ["",               "ov",  "ev"],
                              "pg"  : ["$WORD_BASE%(ext)sa", "i",   "i|$WORD_BASEa", "iju|$WORD_BASEa"],
                             }

        self._add_suffixes("A-M0")
        # A-M0//0 M#A01 N##A-M0//0(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # A-M0//1 M#A02 N##A-M0//1(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # A-M0//2 M#A03 N##A-M0//2(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # A-M0//3 M#A04 N##A-M0//3(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # A-M0/ov/0 M#A05 N##A-M0/ov/0(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # A-M0/ov/1 M#A06 N##A-M0/ov/1(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # A-M0/ov/2 M#A07 N##A-M0/ov/2(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # A-M0/ov/3 M#A08 N##A-M0/ov/3(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # A-M0/ev/0 M#A09 N##A-M0/ev/0(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # A-M0/ev/1 M#A010 N##A-M0/ev/1(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # A-M0/ev/2 M#A011 N##A-M0/ev/2(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # A-M0/ev/3 M#A012 N##A-M0/ev/3(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # A-M0/es/0 M#A013 N##A-M0/es/0(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # A-M0/es/1 M#A014 N##A-M0/es/1(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # A-M0/es/2 M#A015 N##A-M0/es/2(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # A-M0/es/3 M#A016 N##A-M0/es/3(Broj/Padez (deklinacija), 14 suffixes, based_on=)

        self._SUFFIX_TEMPL["A-Moe"] = """ 
                               ##   SINGULAR
                               ##   M
                               ##   ----------
                               #N   $word_base0
                               #G   a
                               #D   u
                               #A   a|$word_base0    ##   NOTE: live / not live
                               #V   $word_base0
                               #L   u
                               #I   %(si)s
                               ## 
                               ##   PLURAL
                               ##   -------------
                               #N   %%S%(ext)si
                               #G   %(ext)sa
                               #D   %%S%(ext)sima
                               #A   %(ext)se
                               #V   %%S%(ext)si
                               #L   %%S%(ext)sima
                               #I   %%S%(ext)sima
                               """

        self.PARAMS_ADD["A-Moe"] = { "ext" : ["",        "ov", "ev"],
                                "si"  : ["$WORD_BASEm", "om", "em"],
                             }

        self._add_suffixes("A-Moe")
        # A-Moe//0 M#Aoe1 N##A-Moe//0(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # A-Moe//1 M#Aoe2 N##A-Moe//1(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # A-Moe//2 M#Aoe3 N##A-Moe//2(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # A-Moe/ov/0 M#Aoe4 N##A-Moe/ov/0(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # A-Moe/ov/1 M#Aoe5 N##A-Moe/ov/1(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # A-Moe/ov/2 M#Aoe6 N##A-Moe/ov/2(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # A-Moe/ev/0 M#Aoe7 N##A-Moe/ev/0(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # A-Moe/ev/1 M#Aoe8 N##A-Moe/ev/1(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # A-Moe/ev/2 M#Aoe9 N##A-Moe/ev/2(Broj/Padez (deklinacija), 14 suffixes, based_on=)

        # TODO: get rid of _suffixes_moe usage
        # ex. "N##A.MOE.SN-oe"
        _suffixes_moe = self.get_suffixes("N##A-Moe//0")


        # TODO: str 104/105 when it is applied - list of words, when sibilarization is not done, etc.

        # --------------- a sklonidba - srednji rod - neproširena i proširena osnova---------------------
        # neutral (srednji rod) - proširena i neproširene osnove
        # check this if should be 
        # TODO: PG %%Aa|%(ext)sa -> %%A%(ext)sa
        # TODO: remove? SI   $WORD_BASEm
        # proširene 3 - kao neproširena samo s nekim razlikama - nema nepostojanog A

        # TODO: p. 107, t.204 - exception is jaje, no ext in plural
        self._SUFFIX_TEMPL["A-N"] = """
                               ##   SINGULAR
                               ##   M
                               ##   ----------
                               #N   $word_base0
                               #G   %(ext)sa
                               #D   %(ext)su
                               ## NOTE: live / not live
                               #A   %(ext)sa|$word_base0
                               #V   $word_base0
                               #L   %(ext)su
                               ##I NOTE: removed $WORD_BASEm|
                               #I   %(ext)som|em
                               ## 
                               ##   PLURAL
                               ##   -------------
                               #N   %%S%(ext)sa
                               #G   %%A%(ext)sa|%(ext)sa
                               #D   %%S%(ext)sima
                               #A   %(ext)sa
                               #V   %%S%(ext)sa
                               #L   %%S%(ext)sima
                               #I   %%S%(ext)sima
                               """

        # TODO: es is not often?, 
        # self.PARAMS_ADD["A-N"] = { "ext" : "es"
        #                              0   1     2     3
        self.PARAMS_ADD["A-N"] = { "ext" : ["", "en", "et"],
                              #"si"  : ["$WORD_BASEm", "om", "em"],
                             }
        self._add_suffixes("A-N")
        # TODO: A.N-0 -> A-N//0
        # self.add_suffixes("", "MANY", "A.N-0", "N#AE4",
        #                        suffixes_force=_suffixes_moe.copy(name="N#__dummy__",
        #                        exceptions={"P/G" : ["a"], "P/A" : ["a"], "P/V" : ["a"]}))
        # A-N//   N#A1 N##A-N//(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # A-N/en/ N#A2 N##A-N/en/(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # A-N/et/ N#A3 N##A-N/et/(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # A-N/es/ N#A4 N##A-N/es/(Broj/Padez (deklinacija), 14 suffixes, based_on=)


        # ----------------- E sklonidba -----------------------------
        # ženske nominativ - završava na a
        # TODO: exception S/DL Hrvatskoj - as adjectives, t.205, p.108
        # TODO: *ha nearly all don't apply S - but in some cases should, 
        #       t.207, p. 108 (svrha - svrsi/svrhi)
        # TODO: exception ruku, nogu, slugu - only with u in pg
        # TODO: exception mati - matere
        self._SUFFIX_TEMPL["E-F"] = """
                               ##   SINGULAR
                               ##   M
                               ##   ----------
                               #N   $word_base0
                               #G   e
                               ## TODO: neki provode sibilarizaciju a neki ne
                               #D   %%Si|i
                               #A   u|$word_base0   ## NOTE: live / not live
                               ## NOTE: |e|a
                               #V   %(sv)s          
                               ## TODO: neki provode sibilarizaciju a neki ne
                               #L   %%Si|i
                               #I   om
                               ## 
                               ##   PLURAL
                               ##   -------------
                               #N   e
                               ## NOTE: %%A - nekad da a nekad ne
                               #G   %(pg)s
                               #D   ama
                               #A   e
                               #V   e
                               #L   ama
                               #I   ama
                               """
        # TODO: es is not often?
        #                              0    1      2      3
        self.PARAMS_ADD["E-F"] = { "ext" : [""],
                              "pg"  : ["a", "%Aa", "%Au", "%Ai", "i"],
                              "sv"  : ["o", "e",   "a"],
                             }
        self._add_suffixes("E-F")

        _suffixes_efn = self.get_suffixes("N##E-F//0/0")
        # E-F//0/0 F#E1 N##E-F//0/0(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # E-F//0/1 F#E2 N##E-F//0/1(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # E-F//0/2 F#E3 N##E-F//0/2(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # E-F//1/0 F#E4 N##E-F//1/0(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # E-F//1/1 F#E5 N##E-F//1/1(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # E-F//1/2 F#E6 N##E-F//1/2(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # E-F//2/0 F#E7 N##E-F//2/0(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # E-F//2/1 F#E8 N##E-F//2/1(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # E-F//2/2 F#E9 N##E-F//2/2(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # E-F//3/0 F#E10 N##E-F//3/0(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # E-F//3/1 F#E11 N##E-F//3/1(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # E-F//3/2 F#E12 N##E-F//3/2(Broj/Padez (deklinacija), 14 suffixes, based_on=)

        # muške po a i e sklonidbi - dubrovački govor ;) - Pero, braco
        # t217, str 112, muški s o i e završavaju, idu po e i a sklonidbi

        # NOTE: not done like other - left as it is - and it works
        # new_object.suffixes = self.union_suffixes(self.suffixes, suffixes_obj_other.suffixes)
        self.add_suffixes("", "MANY", "EA-Moe", "M#EA",
                               suffixes_force=_suffixes_efn.union(name="N##EA-Moe",
                                   suffixes_obj_other=_suffixes_moe))

        # ----------------- I sklonidba -----------------------------
        # ženske nominativ - završava na 0, premda ih je većina na i, 
        # u knjizi (str 114, t219) ne spominje se sibilarizacija
        # radost
        # TODO: exception - kći - kćeri, bol -> bolju, bolovi (mixed decl)
        self._SUFFIX_TEMPL["I-F"] = """
                               ##   SINGULAR
                               ##   M
                               ##   ----------
                               #N   $word_base0
                               #G   i
                               ## TODO: neki provode sibilarizaciju a neki ne %%S?
                               #D   i           
                               ## NOTE: live / not live not appl.
                               #A   $word_base0     
                               ## NOTE: |e|a
                               #V   i          
                               #L   i
                               #I   %(si)s
                               ## 
                               ##   PLURAL
                               ##   -------------
                               #N   i
                               #G   %(pg)s
                               #D   ima
                               #A   i
                               #V   i
                               #L   ima
                               #I   ima
                               """
        # TODO: es is not often?
        #                              0        1      2      3
        self.PARAMS_ADD["I-F"] = { "ext" : [""],
                              "pg"  : ["i",    "i|iju"],
                              "si"  : ["ju|i", "u|i"],
                             }
        self._add_suffixes("I-F")
        # I-F//0/0 F#I1 N##I-F//0/0(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # I-F//0/1 F#I2 N##I-F//0/1(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # I-F//1/0 F#I3 N##I-F//1/0(Broj/Padez (deklinacija), 14 suffixes, based_on=)
        # I-F//1/1 F#I4 N##I-F//1/1(Broj/Padez (deklinacija), 14 suffixes, based_on=)

        # _suffixes_ifn = self.add_suffixes("", "MANY", "I.F.N-0", "F#I1", -> 00
        #                                   (base.ATTR_NUMBER, base.ATTR_DECLINATION),
        # # noć
        # strange P/G is same as in ifn - not exception
        # self.add_suffixes("", "MANY", "I.F.N-0/SI-u", "F#I2",            -> 01
        #                        suffixes_force=_suffixes_ifn.copy(name="N#__dummy__",
        #                           exceptions={"S/I" : ["u", "i"], "P/G" : ["i"]}))
        # # kokoš
        # self.add_suffixes("", "MANY", "I.F.N-0/PG-iju", "F#I3",          -> 10
        #                        suffixes_force=_suffixes_ifn.copy(name="N#__dummy__",
        #                           exceptions={"P/G" : ["i", "iju"]}))
        # TODO: kćer - kćeri ...


    def iter_param_combinations(self, gender_none=False, iter_spec_ext=False):
        """
        >>> iter_params = list(WORD_TYPE.iter_param_combinations(iter_spec_ext=True)) # gender_none=True, 
        >>> len(iter_params) # doctest: +NORMALIZE_WHITESPACE
        86
        >>> sorted(iter_params[:5]) # doctest: +NORMALIZE_WHITESPACE
        [('A-M0D/+A/MG/#E/0S', {'GEN': 'M'}, {'decl': 'A-M0', 'gender': 'M', 'ext': '', 'apply_vc_a': True, 'spec': '0'}), 
         ('A-M0D/+A/MG/#E/1S', {'GEN': 'M'}, {'decl': 'A-M0', 'gender': 'M', 'ext': '', 'apply_vc_a': True, 'spec': '1'}), 
         ('A-M0D/+A/MG/#E/2S', {'GEN': 'M'}, {'decl': 'A-M0', 'gender': 'M', 'ext': '', 'apply_vc_a': True, 'spec': '2'}), 
         ('A-M0D/+A/MG/#E/3S', {'GEN': 'M'}, {'decl': 'A-M0', 'gender': 'M', 'ext': '', 'apply_vc_a': True, 'spec': '3'}), 
         ('A-M0D/+A/MG/ovE/0S', {'GEN': 'M'}, {'decl': 'A-M0', 'gender': 'M', 'ext': 'ov', 'apply_vc_a': True, 'spec': '0'})]

        # >>> list(Noun.iter_param_combinations(gender_none=True))

        >>> list(WORD_TYPE.iter_param_combinations()) # doctest: +NORMALIZE_WHITESPACE
        [('A-M0D/+A/MG/$E/$S', {'GEN': 'M'}, {'decl': 'A-M0', 'gender': 'M', 'ext': None, 'apply_vc_a': True, 'spec': None}), 
         ('A-M0D/-A/MG/$E/$S', {'GEN': 'M'}, {'decl': 'A-M0', 'gender': 'M', 'ext': None, 'apply_vc_a': False, 'spec': None}), 
         ('A-MoeD/+A/MG/$E/$S', {'GEN': 'M'}, {'decl': 'A-Moe', 'gender': 'M', 'ext': None, 'apply_vc_a': True, 'spec': None}), 
         ('A-MoeD/-A/MG/$E/$S', {'GEN': 'M'}, {'decl': 'A-Moe', 'gender': 'M', 'ext': None, 'apply_vc_a': False, 'spec': None}), 
         ('E-FD/+A/FG/$E/$S', {'GEN': 'F'}, {'decl': 'E-F', 'gender': 'F', 'ext': None, 'apply_vc_a': True, 'spec': None}), 
         ('E-FD/-A/FG/$E/$S', {'GEN': 'F'}, {'decl': 'E-F', 'gender': 'F', 'ext': None, 'apply_vc_a': False, 'spec': None}), 
         ('I-FD/+A/FG/$E/$S', {'GEN': 'F'}, {'decl': 'I-F', 'gender': 'F', 'ext': None, 'apply_vc_a': True, 'spec': None}), 
         ('I-FD/-A/FG/$E/$S', {'GEN': 'F'}, {'decl': 'I-F', 'gender': 'F', 'ext': None, 'apply_vc_a': False, 'spec': None}), 
         ('A-ND/+A/NG/$E/$S', {'GEN': 'N'}, {'decl': 'A-N', 'gender': 'N', 'ext': None, 'apply_vc_a': True, 'spec': None}), 
         ('A-ND/-A/NG/$E/$S', {'GEN': 'N'}, {'decl': 'A-N', 'gender': 'N', 'ext': None, 'apply_vc_a': False, 'spec': None})] 

        """
        gender_list = ["M", "F", "N"]
        if gender_none:
            raise NotImplementedError("decl should be iterated through all?? - no need for this now")
            gender_list.insert(0, None)
        for gender in gender_list:
            # TODO: for some decl some combinations are not possible
            #       for real usage - from 3x3 only 4 are possible
            for decl, decl_vals in self.get_params_add_for_gender(gender):
                attrs_fix = {"GEN":gender} 
                for apply_vc_a in (True, False):
                    if gender is None: # not in action
                        params_init = {"apply_vc_a" : apply_vc_a, 
                                       "gender"     : None, 
                                       "decl"       : decl, 
                                       "ext"        : None, 
                                       "spec"       : None,}
                        yield Noun.params2key(params_init), attrs_fix, params_init 
                    elif iter_spec_ext:
                        # TODO: do this with drying 
                        iter_base = [len(v) for k,v in sorted(decl_vals.iteritems()) if k!="ext"]
                        for ext in decl_vals["ext"]:
                            for combination in iter_mine(*iter_base):
                                spec = "".join(["%d" % v for v in combination])
                                params_init = {"apply_vc_a" : apply_vc_a, 
                                               "gender"     : gender, 
                                               "decl"       : decl, 
                                               "ext"        : ext, 
                                               "spec"       : spec,}
                                yield Noun.params2key(params_init), attrs_fix, params_init 
                    else:
                        params_init = {"apply_vc_a" : apply_vc_a, 
                                       "gender" : gender, 
                                       "decl" : decl, 
                                       "ext" : None, 
                                       "spec" : None,}
                        yield Noun.params2key(params_init), attrs_fix, params_init 


    def __init_wts(self):
        # TODO: negdje sam stavljao po dva nastavka a to je u principu nepostojano a u drugom slučaju
        # Muškog roda
        # VR", "vršitelj radnje
        self._add_wts({"GEN":"M"}, "ac"   ,   1, "vr", "", "pisac", apply_vc_a=True)
        self._add_wts({"GEN":"M"}, "ač"    ,   3, "vr", "ie cijepati->", "cjepač")
        self._add_wts({"GEN":"M"}, "ar"    ,  -1, "vr", "ie mlijeko->", "mljekar")
        self._add_wts({"GEN":"M"}, "jar"   ,  -1, "vr", "ie mlijeko->", "mljekar", vc_list="J")
        self._add_wts({"GEN":"M"}, "ič"    ,   0, "vr", "LIST:", "branič,gonič,vodič,ribič")
        self._add_wts({"GEN":"M"}, "lac"   ,   0, "vr", "ie/je, from infinitive, telj", "mislilac")
        self._add_wts({"GEN":"M"}, "telj"  ,   3, "vr", "ie/je, from infinitive, telj", "mislilac")
        # PR", "imenica s osobinom izrečenu pridjevom", "pridjevna osnova
        self._add_wts({"GEN":"M"}, "ac"   ,   1, "PR", "", "krivac, aristotelovac", apply_vc_a=True)
        # OS", "ostalo", "različite osnove
        self._add_wts({"GEN":"M"}, "ak"    ,   2, "os", "", "čudak, imenjak, zemljak") # apply_vc_a=False
        self._add_wts({"GEN":"M"}, "jak"   ,   2, "os", "", "čudak, imenjak, zemljak", apply_vc_a=False) # nj and lj not in our vc_J change , vc_list="J")
        self._add_wts({"GEN":"M"}, "an"    ,   1, "os", "osjećajno", "blesan, tupan, sirotan")
        self._add_wts({"GEN":"M"}, "anin"  ,   1, "os", "(etnici) i opće gdje žive", "goranin, državljanin, građanin")
        self._add_wts({"GEN":"M"}, "aš"    ,   2, "os", "osjećajno, sportaši i zanimanja", "laktaš, nogometaš, velikaš")
        self._add_wts({"GEN":"M"}, "džija" ,   1, "os", "GP osjećajno, turskog podrijetla, zanimanja", "ćevabdžija, galamdžija, račundžija", vc_list="M|Z")
        self._add_wts({"GEN":"M"}, "ić"    ,   0, "os", "(umanjenice) i podrijetlo/srodstvo", "bratić, banović, Kovačević")
        self._add_wts({"GEN":"M"}, "ik"    ,  -1, "os", "nositelj osobine, od VA PAS *n", "mučenik, dužnik, isposnik")
        self._add_wts({"GEN":"M"}, "ist"   ,  -1, "os", "stranog podrijetla", "automobilist, biciklist, novelist")
        self._add_wts({"GEN":"M"}, "ista"  ,  -1, "os", "stranog podrijetla", "automobilist, biciklist, novelist")
        self._add_wts({"GEN":"M"}, "iša"   ,   0, "os", "LIST:","hvališa, platiša, radiša, štediša")
        self._add_wts({"GEN":"M"}, "lija"  ,   0, "os", "turskog i osjećajno", "zanatlija, fakutetlija")
        self._add_wts({"GEN":"M"}, "nik"   ,   0, "os", "LIST:", "bilježnik, liječnik, vijećnik, prokletnik")
        self._add_wts({"GEN":"M"}, "onja"  ,  -1, "os", "osjećajno i porugljivo", "mlakonja, brkonja, sivonja")
        # Ženskog roda
        # MR", "tvore se od osnova imenica muškog roda
        self._add_wts({"GEN":"F"}, "ica"   ,   3, "M", "", "beračica, vozačica") 
        self._add_wts({"GEN":"F"}, "inja"  ,   2, "M", "", "junakinja, nećakinja") 
        self._add_wts({"GEN":"F"}, "kinja" ,   1, "M", "", "sluškinja, vojvotkinja, ropkinja", vc_list="Z") 
        self._add_wts({"GEN":"F"}, "ka"    ,  -1, "M", "", "bolničarka, kršćanka", vc_list="Z") 
        self._add_wts({"GEN":"F"}, "a"     ,   0, "M", "", "kuma, nećaka") 
        # OS", "slabo plodni
        self._add_wts({"GEN":"F"}, "ača"   ,   1, "os", "", "narikača, udavača") 
        self._add_wts({"GEN":"F"}, "ara"   ,   1, "os", "", "gitara, plutara") 
        self._add_wts({"GEN":"F"}, "ična"  ,   1, "os", "", "sestrična, gospodična") 
        self._add_wts({"GEN":"F"}, "ka"    ,   0, "os", "", "plavka", vc_list="Z") 
        self._add_wts({"GEN":"F"}, "kinja" ,   1, "os", "", "dvorkinja, jezerkinja", vc_list="Z") 
        self._add_wts({"GEN":"F"}, "ojka"  ,   1, "os", "", "crnojka, plavojka") 
        self._add_wts({"GEN":"F"}, "ulja"  ,   1, "os", "osjeć.", "mahnitulja, pobjegulja") 
        self._add_wts({"GEN":"F"}, "uša"   ,   1, "os", "osjeć.", "govoruša, namiguša") 
        # MF", "muškog i ženskog roda
        # NOTE: declination is "F" - self._add_wts({"GEN":"M"}, "ica"   ,   1, "MF", "", "izjelica, propalica") 
        # TODO: this is duplicate, need two?
        self._add_wts({"GEN":"F"}, "ica"   ,   1, "MF", "", "izjelica, propalica") 
        # MN", "muški 
        self._add_wts({"GEN":"M"}, "lo"    ,   1, "MN", "osjeć.", "blebetalo, sviralo") 
        self._add_wts({"GEN":"N"}, "lo"    ,   1, "MN", "osjeć.", "blebetalo, sviralo") 
        # Srednjeg roda", "GP
        self._add_wts({"GEN":"N"}, "e"     ,   1, "os", "c/k->če", "bjegunče, unuče") 
        self._add_wts({"GEN":"N"}, "če"    ,   1, "os", "GP ostali", "siroče, slušće", vc_list="Z|P|D")
        # M", "etnici
        self._add_wts({"GEN":"M"}, "ac"   ,   2, "et", "", "Ogulinac, Indijac", apply_vc_a=True) 
        self._add_wts({"GEN":"M"}, "anac" ,   2, "et", "", "Belgijanac, Afrikanac", apply_vc_a=True) 
        # TODO: check what %j means
        self._add_wts({"GEN":"M"},"anin"   ,   2, "et", "", "Gospićanin, Riječanin, Rimljanin") 
        self._add_wts({"GEN":"M"},"janin"  ,   2, "et", "", "Gospićanin, Riječanin, Rimljanin", vc_list="J") 
        self._add_wts({"GEN":"M"},"ak"     ,   0, "et", "", "Bošnjak, Tuzlak") 
        self._add_wts({"GEN":"M"},"jak"    ,   0, "et", "", "Bošnjak, Tuzlak") 
        self._add_wts({"GEN":"M"},"čanin"  ,   1, "et", "", "Zagrebčanin, Drvarčanin") 
        self._add_wts({"GEN":"M"},"lija"   ,   0, "et", "", "Maglajlija, Bečlija") 
        # F", "etnici
        self._add_wts({"GEN":"F"},"ka"     ,   2, "et", "", "Eskimka, Slavenka", vc_list="Z")
        self._add_wts({"GEN":"F"},"kinja"  ,   2, "et", "", "Francuskinja, Kineskinja", vc_list="Z")
        self._add_wts({"GEN":"F"},"inja"   ,   2, "et", "", "Bošnjakinja, Čehinja") 
        self._add_wts({"GEN":"F"},"ica"    ,   2, "et", "", "Hrvatica, Njemica") 
        # TODO: ovdje sam odustao od vc_list", "jer pravila su uvijek ista ... to se može dobiti automatski
        #       kandidati su: k, b, č, d, n, ... i ostali suglasnici koji mogu sudjelovati u glasovnim promjenama
        # zv", "životinje
        self._add_wts({"GEN":"M"},"ac"   ,   1, "zv", "", "bijelac, gnjurac", apply_vc_a=True) 
        self._add_wts({"GEN":"M"},"bać"    ,   0, "zv", "", "zelembać") 
        self._add_wts({"GEN":"N"},"če"     ,   1, "zv", "", "golupče, pašče") 
        self._add_wts({"GEN":"M"},"dać"    ,   0, "zv", "", "srndać") 
        self._add_wts({"GEN":"N"},"e"      ,   0, "zv", "", "gušće, mače") 
        self._add_wts({"GEN":"F"},"ka"     ,   1, "zv", "", "bijelka, kvočka") 
        # TODO: this is common for adj. too
        self._add_wts({"GEN":"M"},"an"     ,   1, "zv", "", "gusan, macan") 
        self._add_wts({"GEN":"M"},"onja"   ,   0, "zv", "", "šaronja, sivonja") 
        # TODO: this conflicts with adj. "OV"
        # self._add_wts({"GEN":"M"},"ov"     ,   0, "zv", "", "bjelov, garov") 
        self._add_wts({"GEN":"F"},"uša"    ,   0, "zv", "", "grmuša, kreketuša") 
        self._add_wts({"GEN":"F"},"ulja"   ,   0, "zv", "", "kasulja, plavulja") 
        # bl", "biljke
        self._add_wts({"GEN":"M"},"ac"    ,   1, "bl", "", "krastavac, kakaovac", apply_vc_a=True) 
        self._add_wts({"GEN":"F"},"ača"    ,   1, "bl", "", "cvjetača, papratnjača") 
        self._add_wts({"GEN":"F"},"ara"    ,   0, "bl", "", "jajara, ludara") 
        self._add_wts({"GEN":"F"},"ica"    ,   1, "bl", "", "borovnica, crnica") 
        self._add_wts({"GEN":"F"},"ika"    ,   0, "bl", "", "crnika, ljutika") 
        self._add_wts({"GEN":"F"},"ka"     ,   0, "bl", "", "ranka") 
        self._add_wts({"GEN":"F"},"nica"   ,   1, "bl", "", "borovnica, mliječnica") 
        self._add_wts({"GEN":"F"},"ulja"   ,   0, "bl", "", "rosulja, vlasulja") 
        # Stvari
        # TODO: make new attr", "metadata about word_type and way on which new word is based
        # o[N|A|V|_]", "oruđa, od imen., gl., pridjevnih osnova, ili svih
        self._add_wts({"GEN":"M"},"ač"     ,  -1, "oV", "", "dubač, nosač") 
        self._add_wts({"GEN":"F"},"ača"    ,  -1, "o-", "", "drljača, zubača") 
        self._add_wts({"GEN":"F"},"aljka"  ,  -1, "oN", "", "kapaljka, kazaljka") 
        self._add_wts({"GEN":"N"},"lo"     ,   2, "oV", "", "mjerilo, kuhalo") 
        self._add_wts({"GEN":"F"},"lica"   ,   2, "oV", "", "bušilica, dizalica") 
        # oo", "ostale ostale stvari
        self._add_wts({"GEN":"M"},"ac"     ,   1, "oo", "", "mamac, slanac", apply_vc_a=True) 
        # TODO: od kojih osnova
        self._add_wts({"GEN":"M"},"ač"     ,  -1, "oo", "", "naslonjač, ogrtač") 
        self._add_wts({"GEN":"F"},"ača"    ,  -1, "oo", "", "brezovača") 
        self._add_wts({"GEN":"F"},"aća"    ,  -1, "oo", "LIST:", "mokraća") 
        # TODO: check - don't apply džak nepostojano a
        self._add_wts({"GEN":"M"},"ak"    ,  -1, "oo", "", "čvarak, džak", apply_vc_a=True) 
        # TODO: check ak in ak/jak 
        self._add_wts({"GEN":"M"},"ak"     ,  -1, "oo", "", "čvarak, džak") 
        self._add_wts({"GEN":"M"},"jak"    ,  -1, "oo", "", "kutnjak, očnjak") 
        self._add_wts({"GEN":"F"},"ica"    ,  -1, "oo", "", "dopisnica, tiskanica") 
        self._add_wts({"GEN":"M"},"ik"     ,  -1, "oo", "", "brojčanik, cjenik") 
        self._add_wts({"GEN":"F"},"ina"    ,  -1, "oo", "", "govedina, janjetina") 
        self._add_wts({"GEN":"N"},"ivo"    ,  -1, "oo", "", "gradivo, cjepivo") 
        self._add_wts({"GEN":"F"},"ka"     ,  -1, "oo", "", "klepka, pečenka") 
        self._add_wts({"GEN":"M"},"aj"     ,   0, "oo", "", "ležaj") 
        self._add_wts({"GEN":"M"},"aš"     ,   0, "oo", "", "paprikaš") 
        self._add_wts({"GEN":"M"},"ež"     ,   0, "oo", "", "crtež") 
        self._add_wts({"GEN":"F"},"iljka"  ,   0, "oo", "", "cjedaljka") 
        self._add_wts({"GEN":"F"},"ište"   ,   0, "oo", "", "grabljište") 
        self._add_wts({"GEN":"N"},"lo"     ,   0, "oo", "", "ogledalo") 
        self._add_wts({"GEN":"F"},"ulja"   ,   0, "oo", "", "žarulja") 
        # mj", "mjesne imenice
        self._add_wts({"GEN":"F"},"ana"    ,   2, "mj", "", "barutana") 
        self._add_wts({"GEN":"F"},"ara"    ,   2, "mj", "", "knjižara") 
        self._add_wts({"GEN":"F"},"arna"   ,   2, "mj", "", "ljekarna") 
        self._add_wts({"GEN":"F"},"nica"   ,   2, "mj", "", "mesnica") 
        self._add_wts({"GEN":"F"},"onica"  ,   2, "mj", "", "čekaonica") 
        self._add_wts({"GEN":"F"},"ija"    ,   1, "mj", "", "županija") 
        self._add_wts({"GEN":"M"},"ik"     ,  -1, "mj", "", "borik") 
        self._add_wts({"GEN":"N"},"ište"   ,  -1, "mj", "", "kukuruzište") 
        self._add_wts({"GEN":"F"},"ština"  ,  -1, "mj", "", "Sloboština") 
        # ms", "mislene imenice
        self._add_wts({"GEN":"F"},"ost"    ,   3, "ms", "", "blagost") 
        self._add_wts({"GEN":"N"},"ostvo"  ,   3, "ms", "", "barbarstvo") 
        self._add_wts({"GEN":"N"},"ilo"    ,  -1, "ms", "", "crvenilo") 
        self._add_wts({"GEN":"F"},"ina"    ,  -1, "ms", "", "brzina") 
        self._add_wts({"GEN":"F"},"oća"    ,  -1, "ms", "", "čistoća") 
        self._add_wts({"GEN":"F"},"ota"    ,  -1, "ms", "", "dobrota") 
        self._add_wts({"GEN":"F"},"otinja" ,   1, "ms", "", "samotinja") 
        self._add_wts({"GEN":"F"},"ština"  ,   1, "ms", "", "lukavština") 
        # V", "glagolske imenice
        self._add_wts({"GEN":"N"},"nje"    ,   3, "V", "", "držanje") 
        self._add_wts({"GEN":"N"},"enje"   ,   3, "V", "", "dopuštenje") 
        self._add_wts({"GEN":"N"},"jenje"  ,   3, "V", "", "otkupljenje") 
        self._add_wts({"GEN":"F"},"a"      ,  -1, "V", "", "kazna") 
        self._add_wts({"GEN":"F"},"aj"     ,  -1, "V", "", "događaj") 
        self._add_wts({"GEN":"F"},"ak"    ,  -1, "V", "", "izlazak", apply_vc_a=True) 
        self._add_wts({"GEN":"F"},"ba"     ,  -1, "V", "", "berba") 
        self._add_wts({"GEN":"F"},"ež"     ,   0, "V", "", "grabež") 
        self._add_wts({"GEN":"F"},"nja"    ,  -1, "V", "", "grdnja") 
        self._add_wts({"GEN":"F"},"ancija" ,  -1, "V", "", "govorancija") 
        self._add_wts({"GEN":"F"},"anija"  ,  -1, "V", "", "pjevanija") 
        # de", "deminutivi", "umanjenice 
        self._add_wts({"GEN":"M"},"ić"      ,  3, "de", "", "kraljić") 
        self._add_wts({"GEN":"M"},"čić"     ,  3, "de", "", "vladarčić") 
        self._add_wts({"GEN":"M"},"ac"    ,  0, "de", "LIST:", "bratac, krušac, staračac", apply_vc_a=True) 
        self._add_wts({"GEN":"M"},"ak"    ,  0, "de", "", "anđelak", apply_vc_a=True) 
        self._add_wts({"GEN":"M"},"ečak",  0, "de", "", "grmečak", apply_vc_a=True) 
        self._add_wts({"GEN":"M"},"ičak",  0, "de", "", "grmičak", apply_vc_a=True) 
        self._add_wts({"GEN":"F"},"ca"      ,  0, "de", "DEKL:", "stvarca") 
        self._add_wts({"GEN":"F"},"čica"    ,  0, "de", "LIST:", "cjevčica, grančica, klupčica, stvarčica") 
        self._add_wts({"GEN":"F"},"ica"     ,  3, "de", "", "crkvica") 
        self._add_wts({"GEN":"N"},"ce"      ,  1, "de", "", "jezerce", base_ends_aeiou=False) 
        self._add_wts({"GEN":"N"},"ance"    ,  1, "de", "", "mjestance") 
        self._add_wts({"GEN":"N"},"ašce"    ,  1, "de", "", "brdašce") 
        self._add_wts({"GEN":"N"},"ence"    ,  1, "de", "", "burence") 
        self._add_wts({"GEN":"N"},"ešce"    ,  1, "de", "", "djetešce") 
        # de", "osnove razl. rodova
        self._add_wts({"GEN":"M"},"eljak"  ,  -1, "de", "", "brdeljak", apply_vc_a=True) 
        self._add_wts({"GEN":"M"},"juljak" ,  -1, "de", "", "čovječuljak", apply_vc_a=True) 
        self._add_wts({"GEN":"M"},"uljak"  ,  -1, "de", "", "crvuljak", apply_vc_a=True) 
        # au", "augmentativi", "uvećanice
        self._add_wts({"GEN":"F"},"ina"    ,  2, "au", "", "junačina") 
        self._add_wts({"GEN":"F"},"čina"   ,  2, "au", "", "prozorčina") 
        self._add_wts({"GEN":"F"},"etina"  ,  2, "au", "", "babetina") 
        self._add_wts({"GEN":"F"},"urina"  ,  2, "au", "", "ptičurina") 
        self._add_wts({"GEN":"F"},"erina"  ,  0, "au", "", "kućerina") 
        self._add_wts({"GEN":"F"},"eskara" ,  0, "au", "", "ljudeskara") 
        self._add_wts({"GEN":"F"},"ešina"  ,  0, "au", "", "glavešina") 
        self._add_wts({"GEN":"F"},"urda"   ,  0, "au", "", "glavurda") 
        self._add_wts({"GEN":"F"},"uskara" ,  0, "au", "LIST:", "babuskara") 
        self._add_wts({"GEN":"F"},"uština" ,  0, "au", "", "baruština") 
        # zb", "zbirne imenice
        self._add_wts({"GEN":"F"},"ad"     ,  2, "zb", "", "prasad") 
        self._add_wts({"GEN":"N"},"je"     ,  3, "zb", "GP", "biserje") 
        self._add_wts({"GEN":"N"},"stvo"   , -1, "zb", "", "seljaštvo") 
        self._add_wts({"GEN":"F"},"arija"  , -1, "zb", "osjeć.", "studentarija") 
        # om", "odmila
        self._add_wts({"GEN":"M"},"ko"     ,  -1, "om", "", "srećko") 
        # TODO: ostale su mi prekomplicirane sada", "digni zadnji slog i dodaj", "a|e|o|ica|ko
        # oz", "ostalih značenjskih skupina
        self._add_wts({"GEN":"F"},"aljka"   ,  -1, "oz", "", "premetaljka") 
        self._add_wts({"GEN":"F"},"arina"   ,  -1, "oz", "", "glavarina") 
        self._add_wts({"GEN":"F"},"arija"   ,  -1, "oz", "", "bljezgarija") 
        self._add_wts({"GEN":"M"},"ak"     ,  -1, "oz", "", "desetak", apply_vc_a=True) 
        self._add_wts({"GEN":"F"},"ina"     ,  -1, "oz", "", "trećina") 
        self._add_wts({"GEN":"F"},"ština"   ,  -1, "oz", "", "štokavština") 

        for key, attrs_fix, params_init in self.iter_param_combinations():
            self._add_wts(attrs_fix, "$BASE$"       ,   -1, key, "", ""  , **params_init)

    def _add_wts(self, attrs_fix, suff_value, freq_type, group, 
                 *args, **kwargs):
        # if suff_value!="$BASE$":
        #     if "apply_vc_a" not in kwargs:
        #         kwargs["apply_vc_a"]=False
        # else:
        #     assert "apply_vc_a" in kwargs
        super(NounType, self)._add_wts(attrs_fix, suff_value, freq_type, group, 
                                       *args, **kwargs)

    def init_wts_forms(self):
        """ NOTE: This is slow ... not called initially
            TODO: this is very similar to adjectives - make it dry
        """
        if self._wts_forms_initialized:
            return

        for code, wts in self.wts_list.iteritems():
            wts_forms = []
            # NOTE: if noun.constructor changes default values - it must be changed here too
            # {"apply_vc_a" : True, "gender" : None, "ext" : "", "spec" : ""}

            gender = wts.attrs_fix["GEN"] #getattr(wts, "gender", None)
            apply_vc_a = getattr(wts, "apply_vc_a", False)
            ext = getattr(wts, "ext", None)
            spec = getattr(wts, "spec", None)
            decl = getattr(wts, "decl", None)
            # TODO: check for each suffix that examples are ok: 
            #       e.g. check "ak" -> "k" but maybe base should be "" ("ak" rule - get ak away)
            # TODO: generate this only for not LIST: - for LIST: don't use suffix but word and mark it like this

            #if apply_vc_a and wts.suff_value.count("a")==1 and wts.suff_value.startswith("a"):
            #    # TODO: iterate for all possible not AEIOU and vocal changes?
            #    # NOTE: is there any case like "ank" - len is 3
            #    assert len(wts.suff_value)==2, wts
            #    # TODO: solve this in wts definition
            #    # apply_vc_a = False
            if wts.desc=="LIST:":
                word_base_list = wts.examples
                status="F" # confirmed - predef word_obj
            else:
                word_base_list = [wts.suff_value]
                status="T" # unconfirmed - suff word_obj
            for word_base in word_base_list:
                noun = Noun(wts.suff_value, gender=gender, 
                            is_suffix = True if status=="T" else False,
                            status=status,
                            apply_vc_a=apply_vc_a, spec=spec, 
                            ext=ext, decl=decl)
                for key, form_list in noun:
                    for ordnr, form in enumerate(form_list):
                        #                 word_obj , suff_key, suff_value))
                        wts_forms.append((noun, key, ordnr+1, form))
            #if wts.suff_value=="ac":
            #    import pdb;pdb.set_trace() 
            # NOTE: this call adds list of wts entries into suff.registry
            wts.add_forms(wts_forms) 
        self._wts_forms_initialized = True
        return

# ----------------------------------------------------------
# TODO: it seems that this is needed when running tests.py
init_logging(fname_log = "nouns.log")

if not base.is_word_type_registred("N"):
    NOUNS         = NounType()
# ----------------------------------------------------------
else:
    NOUNS=base.get_word_type("N")
# ----------------------------------------------------------
WORD_TYPE = NOUNS

def test():
    print "%s: running doctests" % __name__
    import doctest
    doctest.testmod()
    base.run_doctests(( "test_nouns_book.txt"
                       ,"test_nouns-a-m0.txt"
                       ,"test_nouns-a-moe.txt"
                       ,"test_nouns-a-n.txt"
                       ,"test_nouns-e-fa.txt"
                       ,"test_nouns-i-f0.txt"
                       ,"test_nouns_wts.txt"
                      ))

if __name__ == "__main__":
    test()

