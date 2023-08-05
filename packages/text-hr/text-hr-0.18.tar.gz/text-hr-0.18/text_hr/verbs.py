# coding=utf-8
# doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
"""
# TODO: THIS IS SLOW - enable this later

>>> from datetime import datetime, timedelta
>>> started = datetime.now()

>>> WORD_TYPE.init_wts_forms()

>>> ended = datetime.now()

Currently this takes about 1.3 sec on my machine
>>> (ended - started) < timedelta(seconds=3)
True
"""
import base

from morphs import WordSuffixes, WordTypeSuffix, AEIOU, ChangeableWordBase, BadParamsInitError
from morphs import count_wparts, _remove_vc_a, _apply_vc_a, split_by_last_AEIOU
from morphs import uni_prepare, uni_revert, LJ, NJ, DZ
from adjectives import Adjective

from text_hr.utils import to_unicode, init_logging, IterAttrs

# TODO: pasti / padati - svršeni i nesvršeni glagoli - potrebno razlučiti i moguće korigirati prepoznavanje
class Verb(ChangeableWordBase):
    """
    >>> def print_it(params_init):
    ...     key = Verb.params2key(params_init)
    ...     print repr(key), repr(Verb.key2params(key))

    >>> print_it({"ext" : 0})
    '0E' {'ext': '0'}
    >>> print_it({"ext" : "e"})
    'eE' {'ext': 'e'}

    >>> krenuti = Verb("krenuti")
    >>> print krenuti
    W(u'krenuti'=V)

    >>> krenuti.params_key, krenuti.params_key
    ('$E', '$E')
    >>> krenuti.word_base, krenuti.word_lexem_pre, krenuti.word_lexem_inf
    (u'krenuti', u'kren', u'krenu')


    # >>> krenuti.forms_flat

    """
    VA_P_EXCEPTIONS = """+izustiti +premostiti +osvijestiti +omastiti
                         vijestiti vlastiti mjestiti
                         krstiti koristiti  prostiti upropastiti uvrstiti zaprepastiti
                      """.split()
    for word in VA_P_EXCEPTIONS:
        assert word.endswith("stiti")

    ATTR_VALUES_NO_ADJ   = None
    ATTR_VALUES_WITH_ADJ = None

    @classmethod
    def init_attr_values(cls):
        """ tests in test_verbs_type.txt """
        if cls.ATTR_VALUES_NO_ADJ:
            return

        Adjective.init_attr_values()

        cls.ATTR_VALUES_NO_ADJ   = []
        cls.ATTR_VALUES_WITH_ADJ = []

        for extra in ("X_INF", "X_VAD_PRE", "X_VAD_PAS"):
            cls.ATTR_VALUES_NO_ADJ.append((extra, '', ''))
            cls.ATTR_VALUES_WITH_ADJ.append((extra, '', ''))
         
        for time in base.ATTR_TIME.values:
            if time.startswith("VA_"):
                last_loop = base.ATTR_GENDER.values 
            else:
                last_loop = base.ATTR_PERSON.values 
            for num in base.ATTR_NUMBER.values:
                for per_or_gender in last_loop:
                    cls.ATTR_VALUES_NO_ADJ.append((time, num, per_or_gender))
                    cls.ATTR_VALUES_WITH_ADJ.append((time, num, per_or_gender))

        for item in Adjective.ATTR_VALUES_NO_COM:
            # comparation, type_, num, decl, gender
            item_ext = ("VA_PA", "", "+".join(item))
            cls.ATTR_VALUES_WITH_ADJ.append(item_ext)

    # NOTE: When __init__ is changed, then don't forget to update here
    PARAM_NAME_LIST = ["ext"]

    def __init__(self, word_base, 
                 ext=None, # spec=None, 
                 is_suffix=False, #spec_pre=None, 
                 status="T", sri=None, word_type=None):  #apply_vc_a=True, 
        """
        NOTE: When __init__ is changed, then don't forget to params2key here
        NOTE: if NOUNS.constructor changes default values - it must be changed down in wts adding too
        """
        if not word_type:
            # from verbs import VERBS  # found no better way :(
            word_type = VERBS
        assert word_type.code=="V"

        word_base = word_base.strip()
        word_base = to_unicode(word_base)
        self.ext= ext
        if isinstance(self.ext, basestring) and self.ext.isdigit():
            self.ext = int(self.ext)
        #self.spec = spec
        self.is_suffix, self.sri = is_suffix, sri
        assert word_base
        self.is_base_suffix = False

        if not self.ATTR_VALUES_NO_ADJ:
            self.init_attr_values()
        self.attr_values = self.ATTR_VALUES_NO_ADJ if self.is_suffix else self.ATTR_VALUES_WITH_ADJ
        super(Verb, self).__init__(word_type=word_type, word_base=word_base, 
                                   attr_vals_fix=[], is_suffix=is_suffix,
                                   status=status, 
                                   accept_attr_none=True)
        if not is_suffix and len(self.word_base)<3:
            raise BadParamsInitError("%s is too short (ti/chi)" % repr(self.word_base))
        if self.sri:
            assert self.word_base.endswith(self.sri.word_obj.word_base)
            start = self.word_base[:-len(self.sri.word_obj.word_base)]
            # TODO: more rules
            # =="brojjeti": import pdb;pdb.set_trace() 
            if start and start[-1]==self.sri.word_obj.word_base[0]:
                raise BadParamsInitError("%s invalid composing with %s" % (
                        repr(self.word_base), self.sri.word_obj.word_base))

        if self.word_base[-2:]=="ti":
            if len(self.word_base)>=3 and self.word_base[-3] not in AEIOU+"s":
                raise BadParamsInitError("%s should end in '%s'" % 
                        (repr(self.word_base), AEIOU+"s"))
        elif self.word_base[-2:]==unicode("ći", "utf-8"):
            if len(self.word_base)>=3 and self.word_base[-3] not in AEIOU+"r":
                raise BadParamsInitError("%s should end in '%s'" % 
                        (repr(self.word_base), AEIOU+"r"))
        else:
            raise BadParamsInitError("%s doesn't end in (ti/chi)" % repr(self.word_base))

        self.params_init = { "ext" : self.ext }

        assert not self.is_base_suffix
        lexem_list = self.word_type.suggest_lexem(self.word_base, is_suffix=self.is_suffix, 
                                                  match_multi_rules=(self.sri is None))
        assert isinstance(lexem_list, list)
        if self.ext is not None:
            lexem_list_choosen = []
            if isinstance(self.ext, int):
                if len(lexem_list)<=self.ext:
                    raise BadParamsInitError("For %s/%s base got multiple less lexem_list (%s) than ext is (params=%s)" % (
                                                 repr(self.word_base), repr(self.ext), repr(lexem_list_choosen), self.params_init))
                lexem_list_choosen.append(lexem_list[self.ext])
            else:
                for lexem, spec, lexem_inf, lexem_rule in lexem_list:
                    if spec==self.ext:
                        lexem_list_choosen.append((lexem, spec, lexem_inf, lexem_rule))
        else:
            lexem_list_choosen = lexem_list

        choose_ind = 0
        if len(lexem_list_choosen)>1:
            raise BadParamsInitError("For %s/%s base got multiple lexem %s suggestions. Please specify which one to use or iterate over all (params=%s)" % (
                                         repr(self.word_base), repr(self.ext), repr(lexem_list_choosen), self.params_init))
        else:
            if not lexem_list_choosen:
                raise BadParamsInitError("For %s/%s base got no lexem suggestions (list=%s, params=%s)" % (
                                          repr(self.word_base), repr(self.ext), repr(lexem_list), self.params_init))

        self.word_lexem_pre, self.pre_spec, self.word_lexem_inf, self.lexem_rule = lexem_list_choosen[choose_ind]
        if not self.is_suffix and not (self.word_lexem_inf and self.word_lexem_pre):
            raise BadParamsInitError("For %s/%s base got empty lexem data %s (params=%s)" % (
                                         repr(self.word_base), repr(self.ext), repr(lexem_list_choosen[choose_ind]), self.params_init))

        # NOTE: this happens only in 3 cases, ti, ći, sti
        #       if not self.word_lexem_pre or not self.word_lexem_inf: print ...
        if self.ext is None or isinstance(self.ext, int):
            self.ext = self.pre_spec
            # self.params_init["ext"]=self.ext 

        # else:
        #     if self.ext!=self.pre_spec:
        #     raise BadParamsInitError("For %s/%s base got single lexem suggestions with diff ext=%s (list=%s, params=%s)" % (
        #                               repr(self.word_base), repr(self.ext), repr(self.pre_spec), repr(lexem_list), self.params_init))

        # if self.apply_vc_a:
        #     self.word_base  = _remove_vc_a(self.word_base)
        #     self.word_lexem = _apply_vc_a(self.word_base)
        # else:
        #     self.word_lexem = self.word_base
        self.word_lexem = [self.word_lexem_pre, self.word_lexem_inf]
        self.word_base_changed = False


    def _get_forms(self):       self._init_forms(); return self._forms
    def _get_forms_flat(self):  self._init_forms(); return self._forms_flat
    def _get_forms_stats(self): self._init_forms(); return self._forms_stats

    forms_flat  = property(_get_forms_flat  )
    forms       = property(_get_forms       )
    forms_stats = property(_get_forms_stats )

    def pp_forms(self, key_filter=""):
        old_time = ""
        for key, val in self.forms_flat:
            flds = key.split("/")
            #if time and flds[0]!=time:
            if key_filter and not key.startswith(key_filter):
                continue
            new_time = flds[:2] 
            if (old_time!="" and new_time!=old_time):
                print ""
            print "%s %s," % (key, val),
            old_time = new_time
        return

    def _init_forms(self):
        if hasattr(self, "_forms"):
            return
        assert not self.is_base_suffix
        if self.is_suffix:
            assert self.word_base
        else:
            assert self.word_base and self.word_lexem_pre and self.word_lexem_inf

        self._forms = {}
        self._forms["%s//" % "X_INF"]     = [self.word_base]
         
        # TODO: later ...
        self._suffix_dict = {}
        self.lexems_time = {}
        for time in base.ATTR_TIME.values:
            multiple_matchs = None
            word_lexem = None
            ext  = "*"
            spec = "*"
            # TODO: what to do?
            #   AOR - mainly PRE
            #   IMP - both
            #   IMV - most INF; rare PRE
            #   VA_A - INF
            #   VA_P - most INF; rare PRE
            if time=="PRE":
                word_lexem = self.word_lexem_pre
                if self.ext:
                    ext  = self.ext
                    spec = ""
            elif time=="AOR":
                if (    self.word_lexem_pre and self.word_lexem_pre[-1] not in AEIOU 
                    and self.word_lexem_inf and self.word_lexem_inf[-1] in AEIOU):
                    word_lexem = self.word_lexem_inf
                else:
                    word_lexem = self.word_lexem_pre
                if word_lexem:
                    spec = ""
                    ext  = "" if word_lexem and word_lexem[-1] in AEIOU else "o"
            elif time=="IMP":
                word_lexem = self.word_lexem_pre
                if word_lexem:
                    if word_lexem[-1] in AEIOU:
                        ext="j"
                        spec=""
                    # TODO: there should be some rule to see which word_base/lexem match "" and which "ij"
                    # else: ... - all 3 possible
            elif time=="IMV":
                if (   self.word_lexem_pre and self.word_lexem_pre[-1] in "ij"+WordSuffixes.VC_J_CHARLIST_FROM
                   and self.word_lexem_inf and self.word_lexem_inf[-1] not in "ij"+WordSuffixes.VC_J_CHARLIST_FROM
                   and self.ext in ("je", "i")):
                    word_lexem = self.word_lexem_pre
                    if word_lexem and word_lexem[-1] in WordSuffixes.VC_J_CHARLIST_FROM:
                        ext = "ji"
                        spec=""
                else:
                    word_lexem = self.word_lexem_inf

                # TODO: 4 ways - 0, i, j, ji
                if ext=="*" and word_lexem and word_lexem[-1] in "ij":
                    ext = "i" if word_lexem in "i" else ""
                    spec=""

            elif time=="VA_A":
                word_lexem = self.word_lexem_inf
                if word_lexem:
                    ext=""
                    spec = "0" if word_lexem and word_lexem[-1] in AEIOU else "1"
            elif time=="VA_P":
                # esti -> sti, jer imam pasti -> padan
                if self.word_base.endswith("sti"):
                    #self.word_lexem_pre.endswith("et"):
                    word_lexem = self.word_lexem_pre
                else:
                    word_lexem = self.word_lexem_inf

                if self.word_base.endswith("stiti"):
                    # should end with šten
                    both = None
                    for word in self.VA_P_EXCEPTIONS:
                        if word.startswith("+") and self.word_base.endswith(word[1:]):
                            both = True
                            break
                        elif self.word_base.endswith(word):
                            both = False
                            break
                    if both in (True, False):
                        cut_from, add_suffix = len("stiti"), unicode("št", "utf-8")
                        lexem_rule = cut_from, add_suffix
                        word_lexem = self.word_base[:-cut_from]+add_suffix
                        #word_lexem = self.word_base[:-len("stiti")]+unicode("št", "utf-8")
                        ext, spec = "en", ""
                        if both==True:
                            multiple_matchs = [(word_lexem, ext, spec, lexem_rule), 
                                               (self.word_lexem_inf, "jen", "")]
                        else:
                            multiple_matchs = [(word_lexem, ext, spec, lexem_rule)]
                    else:
                        ext, spec = "jen", ""
                else:
                    if self.word_lexem_inf and self.word_lexem_inf[-1] in AEIOU:
                        if self.word_lexem_inf[-1] in "i":
                            ext, spec = "jen", ""
                        else:
                            # TODO: ganun is very strange, nun shouldn't happen
                            #       find some better rules
                            multiple_matchs = [(word_lexem, "n", ""), 
                                               (word_lexem, "t", ""),
                                              ]
                    elif word_lexem:
                        ext, spec = "en", ""
            else:
                raise Exception("bad time %s" % time)

            if multiple_matchs is None:
                assert word_lexem is not None
                multiple_matchs = [(word_lexem, ext, spec)]

            # add lexem_rule
            def add_lexem_rule(word_lexem, ext, spec, lexem_rule=None):
                if lexem_rule is None:
                    if word_lexem==self.word_lexem_pre:
                        lexem_rule=self.lexem_rule
                    else:
                        assert word_lexem==self.word_lexem_inf
                        lexem_rule=None
                item_new = (word_lexem, ext, spec, lexem_rule)
                return item_new

            multiple_matchs = [add_lexem_rule(*item) for item in multiple_matchs]
            self.lexems_time[time] = multiple_matchs

            for i, item in enumerate(multiple_matchs):
                word_lexem, ext, spec, lexem_rule = item

                suffname  = "V##%s/%s/%s" % (time, ext, spec)
                suffix_obj = self.word_type.get_suffixes(suffname)
                sforms, swords = suffix_obj.get_forms(self.word_base, word_lexem)
                if i==0:
                    self._suffix_dict[time] = []
                self._suffix_dict[time].append(suffix_obj)

                for k,v in sforms.iteritems():
                    key = "%s/%s" % (time, k)
                    assert key.count("/")==2, key
                    if i==0:
                        assert key not in self._forms
                        self._forms[key]=[]
                    self._forms[key].extend(v)
                    # cls.ATTR_VALUES.append((time, num, per_or_gender))
                    # for time, num, per_or_gender in self.attr_values:

        # glagolski prilog sadašnji - particip prezenta - only verbs - present for S/3 needed""" 
        time = "X_VAD_PRE"
        if self.word_base=="htjeti":
            v_adv_pre = u"hoteći"
            # TODO: self.lexems_time[time] = [self.word_lexem_pre, "-", "-", (cut_from, add_suffix)]
        elif self.word_base=="biti":
            v_adv_pre = u"budući"
            # TODO: self.lexems_time[time] = [self.word_lexem_pre, "-", "-", (cut_from, add_suffix)]
        else:
            v_adv_pre = self._forms["PRE/P/3"][0] + u'\u0107i'
            if self.lexem_rule:
                # NOTE: cut_from, add_suffix is not good! - from word_base - how to get this form 
                #       apply two lexem_rules - this and self.lexem_pre
                #       aći -> a (-2) + č (+1) - lexem
                #       ač  -> +u (+1 P/3) + ći (+2 VA_PRE)
                #       ačući = -2 + 1 + 1 + 2 (=> -2, + 4)
                cut_from = len(v_adv_pre)-len(self.word_lexem_pre)
                add_suffix = v_adv_pre[-cut_from:]
                cut_from   = self.lexem_rule[0]
                add_suffix = self.lexem_rule[1] + add_suffix
                self.lexems_time[time] = [v_adv_pre, "-", "-", (cut_from, add_suffix)]
            else:
                assert not self.is_suffix
                # TODO: currently don't know better solution
                self.lexems_time[time] = [v_adv_pre, "-", "-", None]
        self._forms["%s//" % time] = [v_adv_pre]

        # glagolski prilog prošli - particip perfekta - only verbs - infinitiv needed
        time = "X_VAD_PAS"
        if self.word_lexem_inf:
            if self.word_lexem_inf[-1] in AEIOU:
                v_adv_pas = [self.word_lexem_inf + u"vši"]
                self.lexems_time[time] = [v_adv_pre, "-", "-", (-len("ti"), u"avši")]
            else:
                v_adv_pas = [self.word_lexem_inf + u"avši"]
                self.lexems_time[time] = [v_adv_pre, "-", "-", (-len("ti"), u"vši")]
        else:
            v_adv_pas = [u"vši", u"avši"]
            # TODO: self.lexems_time[time] = multiple_matchs - what to do?
            self.lexems_time[time] = [v_adv_pre, "-", "-", (-len("ti"), u"vši")]
        self._forms["%s//" % time] = v_adv_pas

        if not self.is_suffix:
            self.lexems_time["VA_PA"] = "is not suffix - shouldn't need this"
            self.words_va_p = []
            for i, lexem_va_p in enumerate(self._forms["VA_P/S/M"]):
                word_obj = Adjective(lexem_va_p,
                                     apply_vc_a=False, 
                                     has_neo=True, 
                                     has_com=False, 
                                     is_suffix=self.is_suffix)
                self.words_va_p.append(word_obj)
                for k, v in word_obj.forms_flat:
                    #'P_O/P/D/F'
                    key = "%s//%s" % ("VA_PA", "+".join(k.split("/")))
                    if i==0:
                        self._forms[key] = []
                    self._forms[key].extend(v)
            # TODO: issue is that this isn't added into forms_flat and other data
            #       this needs to be changed in 
            #           def init_attr_values(cls):
            #       and then I need to have it allways and for suffix too

        self.init_forms_common()

        #if not self.is_base_suffix: 
        assert len(self._forms_flat[0][1])==1, self._forms_flat[0][1]
        if not self.word_base in self._forms_flat[0][1]:
            raise BadParamsInitError("For %s base got lexem %s, but base not same as first form (%s). Maybe params_init is bad, or some vc is missing? (params=%s)" % (
                                      repr(self.word_base), repr(self.word_lexem), 
                                      self._forms_flat[:2], self.params_init))

# define wordtypes", "must be done like this since wtypes is loaded once and this module several times
class VerbType(base.ChangeableWordType):

    def __init__(self):
        super(VerbType, self).__init__("V"  , "Glagoli", 
                                       attrs_ch=[base.ATTR_TIME, base.ATTR_NUMBER, base.ATTR_PERSON])
        
        self.__init_suffixes()
        self.__init_stdwords()
        self.__init_wts()

    def __init_suffixes(self):
        # TODO: sibilarizacija t 298 not done str. 149

        # ------------------- SUFFIXES FOR PRESENT ----------------
        self._SUFFIX_TEMPL["PRE"] = """
                                    ##   SINGULAR
                                    ##   M
                                    ##   ----------
                                    #1   %(ext)sm
                                    #2   %(ext)sš
                                    #3   %(ext)s
                                    ##   PLURAL
                                    ##   -------------
                                    #1   %(ext)smo
                                    #2   %(ext)ste
                                    #3   %(p3)s
                               """
        self.PARAMS_ADD["PRE"] = {
                                  "ext" : {  # ordered dict :(
                                            "01_e"  : {"p3" : "u"},   # tresti -> tresem 
                                            "02_je" : {"p3" : "ju"},  # piti   -> pijem
                                            "03_i"  : {"p3" : "e"},   # raditi -> radim
                                            "04_a"  : {"p3" : "aju"}, # čitati -> čitam
                                          }
                                  }
        
        # print self.get_text("PRE", {"ext": "e"})
        # print self.get_text("PRE", {"ext": "je"})
        # print self.get_text("PRE", {"ext": "i"})
        # print self.get_text("PRE", {"ext": "a"})
        self._add_suffixes("PRE")
        # print self.get_all("PRE")

        # # ------------------- SUFFIXES FOR AORIST ----------------
        self._SUFFIX_TEMPL["AOR"] = """
                                    ##   SINGULAR
                                    ##   M
                                    ##   ----------
                                    #1   %(ext)sh
                                    #2   %(s2)s
                                    #3   %(s3)s
                                    ##   PLURAL
                                    ##   -------------
                                    #1   %(ext)ssmo
                                    #2   %(ext)sste
                                    #3   %(ext)sše
                               """
        self.PARAMS_ADD["AOR"] = {
                                  "ext" : {  # ordered dict :(
                                            "01_o"  : {"s2" : "%Pe", "s3" : "%Pe"},  # 0 dođoh
                                            "02_"   : {"s2" : "0", "s3" : "0"},      # 1 pobijedih
                                          }
                                  }
        # print self.get_text("AOR", {"ext": "o"})
        # print self.get_text("AOR", {"ext": ""})
        # print self.get_text("AOR", {"ext": 0})
        # print self.get_text("AOR", {"ext": 1})
        self._add_suffixes("AOR")
        # print self.get_all("AOR")

        # # ------------------- SUFFIXES FOR IMPERFEKT ----------------
        self._SUFFIX_TEMPL["IMP"] = """
                                    ##   SINGULAR
                                    ##   M
                                    ##   ----------
                                    #1   %(ext)sah
                                    #2   %(ext)saše
                                    #3   %(ext)saše 
                                    ##   PLURAL
                                    ##   -------------
                                    #1   %(ext)sasmo
                                    #2   %(ext)saste
                                    #3   %(ext)sahu
                               """
        self.PARAMS_ADD["IMP"] = {
                                 "ext" : ["", "j", "ij"]
                                 }
        # print self.get_text("IMP", {"ext": ""})
        # print self.get_text("IMP", {"ext": "j"})
        # print self.get_text("IMP", {"ext": "ij"})
        # print self.get_text("IMP", {"ext": 0})
        # print self.get_text("IMP", {"ext": 1})
        # print self.get_text("IMP", {"ext": 2})
        self._add_suffixes("IMP")
        # print self.get_all("IMP")

        # # ------------------- SUFFIXES FOR IMPERATIV ----------------
        self._SUFFIX_TEMPL["IMV"] = """
                                    ##   SINGULAR
                                    ##   M
                                    ##   ----------
                                    #1   -
                                    #2   %(s2)s
                                    #3   -
                                    ##   PLURAL
                                    ##   -------------
                                    #1   %(ext)smo
                                    #2   %(ext)ste
                                    #3   - 
                               """
        self.PARAMS_ADD["IMV"] = {
                                  "ext" : {  # ordered dict :(
                                            "01_"    : {"s2" : "0|i"},  # 0 ?
                                            "02_i"   : {"s2" : "i"},  # 1 nosi
                                            "03_j"   : {"s2" : "j"},  # 2 hodaj
                                            "04_ji"  : {"s2" : "ji"}, # 3 pisji -> piši
                                          }
                                  }

        # print self.get_text("IMV", {"ext": ""})
        # print self.get_text("IMV", {"ext": "i"})
        # print self.get_text("IMV", {"ext": 0})
        # print self.get_text("IMV", {"ext": 1})
        self._add_suffixes("IMV")
        # print self.get_all("IMV")

        # ---------------------- GLAGOLSKI PRIDJEVI - RADNI I TRPNI ------------------ 

        # ------------ glagolski pridjev radni / aktiv ----------------------
        self._SUFFIX_TEMPL["VA_A"] = """
                                     ##   SINGULAR
                                     ##   ----------
                                     #M   %(sm)s
                                     #F   la
                                     #N   lo
                                     ##   PLURAL
                                     ##   -------------
                                     #M   li
                                     #F   le
                                     #N   la 
                                     """
        self.PARAMS_ADD["VA_A"] = {
                                  "ext" : [""],
                                  "sm" : ["o", "ao"]
                                  }

        # print self.get_text("VA_A", {"sm": "o"})
        # print self.get_text("VA_A", {"sm": "ao"})
        # print self.get_text("VA_A", {"sm": 0})
        # print self.get_text("VA_A", {"sm": 1})
        self._add_suffixes("VA_A")
        # print self.get_all("VA_A")

        # # ------------ glagolski pridjev trpni / pasiv ----------------------
        self._SUFFIX_TEMPL["VA_P"] = """
                                     ##   SINGULAR
                                     ##   ----------
                                     #M   %(ext)s
                                     #F   %(ext)sa
                                     #N   %(ext)so 
                                     ##   PLURAL
                                     ##   -------------
                                     #M   %(ext)si
                                     #F   %(ext)se
                                     #N   %(ext)sa
                                     """
        self.PARAMS_ADD["VA_P"] = {
                                  "ext" : ["n", "en", "jen", "t", 
                                           ],
                                  }
        # print self.get_text("VA_P", {"ext": "n"})
        # print self.get_text("VA_P", {"ext": "en"})
        # print self.get_text("VA_P", {"ext": "jen"})
        # print self.get_text("VA_P", {"ext": "t"})
        # print self.get_text("VA_P", {"ext": 0})
        # print self.get_text("VA_P", {"ext": 1})
        # print self.get_text("VA_P", {"ext": 2})
        # print self.get_text("VA_P", {"ext": 3})
        self._add_suffixes("VA_P")
        # print self.get_all("VA_P")


    # ==================== POMOĆNI GLAGOLI BITI/HTJETI/BIVATI ======================
    def __init_stdwords(self):
    # ==============================================================================
        # prvi je naglašeni
        # TODO: 
        _suffixes_pre_em = self.get_suffixes("V##PRE/e/")
        _suffixes_pre_am = self.get_suffixes("V##PRE/a/")
        _suffixes_pre_im = self.get_suffixes("V##PRE/i/")
        _suffixes_pre_jem= self.get_suffixes("V##PRE/je/")
        _suffixes_aor_h  = self.get_suffixes("V##AOR//")
        _suffixes_aor_oh  = self.get_suffixes("V##AOR/o/")
        _suffixes_imp_ijah= self.get_suffixes("V##IMP/ij/")
        _suffixes_va_act_o= self.get_suffixes("V##VA_A//0")
        _suffixes_va_pas_n= self.get_suffixes("V##VA_P/n/")
        _suffixes_imv_i   = self.get_suffixes("V##IMV/i/")

        self._suffixes_pre_biti_nag = self.add_suffixes("PRE", "SINGLE", "biti/NAG", "",
                               (base.ATTR_NUMBER, base.ATTR_PERSON),
                                 u"""##   SINGULAR
                                 ##   M
                                 ##   ----------
                                 #1   am
                                 #2   i
                                 #3   st
                                 ##   PLURAL
                                 ##   -------------
                                 #1   mo
                                 #2   te
                                 #3   u
                             """)
        # drugi je nenaglašeni
        self._suffixes_pre_biti_nen = self.add_suffixes("PRE", "SINGLE", "biti/NEN", "",
                               (base.ATTR_NUMBER, base.ATTR_PERSON),
                                 u"""##   SINGULAR
                                 ##   M
                                 ##   ----------
                                 #1   am
                                 #2   i
                                 #3   -1je
                                 ##   PLURAL
                                 ##   -------------
                                 #1   mo
                                 #2   te
                                 #3   u
                             """)

        # ------------ htjeti ----------------------
        # prvi je naglašeni
        self._suffixes_pre_htjeti = self.add_suffixes("PRE", "SINGLE", "htjeti", "",
                               (base.ATTR_NUMBER, base.ATTR_PERSON),
                                 u"""##   SINGULAR
                                 ##   M
                                 ##   ----------
                                 #1   u
                                 #2   eš
                                 #3   e
                                 ##   PLURAL
                                 ##   -------------
                                 #1   emo
                                 #2   ete
                                 #3   e
                             """)

        # TODO: svršeni glagoli 
        #       - oh upotrebljavaju koji imaju osnova je na zatvornik - dići, dig-oh, izgrepsti, izgreb-ah, uvedoh
        #       - h kojima inf. osnova na infinitiv - čuti - ćuh, kazati -> kazah, otpiti - otpih
        # prvi je naglašeni
        self._suffixes_aor_biti = self.add_suffixes("AOR", "SINGLE", "biti", "",
                               (base.ATTR_NUMBER, base.ATTR_PERSON),
                                 u"""##   SINGULAR
                                 ##   M
                                 ##   ----------
                                 #1   ih
                                 #2   i
                                 #3   i
                                 ##   PLURAL
                                 ##   -------------
                                 #1   ismo
                                 #2   iste
                                 #3   iše|i ## unified nen and nag
                             """)

        # ------------ htjeti ----------------------
        # prvi je naglašeni
        # TODO: NOT NEEDED??
        # self._suffixes_aor_htjeti = self.add_suffixes("AOR", "SINGLE", "htjeti", 
        #                        (base.ATTR_NUMBER, base.ATTR_PERSON),
        #                          u"""##   SINGULAR
        #                          ##   M
        #                          ##   ----------
        #                          #1   oh
        #                          #2   e
        #                          #3   e
        #                          ##   PLURAL
        #                          ##   -------------
        #                          #1   osmo
        #                          #2   oste
        #                          #3   oše
        #                      """)

        word_biti = self.add_word("biti")
        word_bivati = self.add_word("bivati")
        word_htjeti = self.add_word("htjeti")
        word_biti.add_forms("jes", "PRE", self._suffixes_pre_biti_nag, attr_extra="NAG")


        word_biti.add_forms("s", "PRE", self._suffixes_pre_biti_nen, attr_extra="NEN")

        # treći je niječni - nema ga u knjizi 
        # TODO: javi u knjizi
        word_biti.add_forms("nis", "PRE", self._suffixes_pre_biti_nen, attr_extra="NIJ") # NIJ

        # Četvrti je dvovidni
        word_biti.add_forms("bud", "PRE", _suffixes_pre_em, attr_extra="DVO")

        # ------------ bivam - u prezentu -------------
        word_bivati.add_forms("biv", "PRE", _suffixes_pre_am)

        word_htjeti.add_forms(u"hoć", "PRE", self._suffixes_pre_htjeti, attr_extra="NAG")
        # drugi je nenaglašeni
        word_htjeti.add_forms(u"ć", "PRE", self._suffixes_pre_htjeti, attr_extra="NEN")
        # treći je nijekani 
        word_htjeti.add_forms(u"neć", "PRE", self._suffixes_pre_htjeti, attr_extra="NIJ")

        word_biti.add_forms(u"b", "AOR", self._suffixes_aor_biti)

        word_htjeti.add_forms(u"htjed", "AOR", _suffixes_aor_oh)

        # pomoćni glagoli
        # 
        # TODO: onaj arhaični oblik nisam bjeh, bješe
        word_biti.add_forms(u"b", "IMP", _suffixes_imp_ijah)
        # ------------ htjeti ----------------------
        # TODO: onaj arhaični oblik nisam hoćah, hoćaše
        word_htjeti.add_forms(u"ht", "IMP", _suffixes_imp_ijah)
        # pomoćni glagoli

        # TODO: onaj arhaični oblik nisam bjeh, bješe
        self._suffixes_imv_biti_i = self.add_suffixes("IMV", "SINGLE", "biti/-i", "",
                                      suffixes_force = _suffixes_imv_i.copy(name="V#__dummy__",
                                      exceptions = {"S/3" : ["e"], "P/3" : ["u"]}))

        # NOTE: S/3 and P/3 is "neka bude", "neka budu"
        word_biti.add_forms(u"bud", "IMV", self._suffixes_imv_biti_i)


        # NOTE: should I add these words to VA too. Think not for now.
        word_biti.add_forms("bi", "VA_A", _suffixes_va_act_o) #, word_type_conv_str="VA")
        word_htjeti.add_forms("htje", "VA_A", _suffixes_va_act_o) #, word_type_conv_str="VA")

        # ------------ std i česte riječi - verbs freq --------------------
        # for moći, mogu, mogješ (možeš)
        self._suffixes_pre_morati_jem = self.add_suffixes("PRE", "SOME", "morati/-jem", "",
                                            suffixes_force=_suffixes_pre_jem.copy(name="V#__dummy__",
                                                  exceptions={"S/1" : ["u"]}))

        # add VA 
        # TODO: encode with unicode()
        _freq_words_data = {"morati"  : {"lexem_PRE" : "mor" ,"lexem" : "mora"  , "SUFF_PRE" : _suffixes_pre_am              , "SUFF_AOR" : _suffixes_aor_h, "SUFF_VA_A" : _suffixes_va_act_o, "SUFF_VA_P" : None }, 
                            "trebati" : {"lexem_PRE" : "treb","lexem" : "treba" , "SUFF_PRE" : _suffixes_pre_am              , "SUFF_AOR" : _suffixes_aor_h, "SUFF_VA_A" : _suffixes_va_act_o, "SUFF_VA_P" : None }, 
                            u"željeti": {"lexem_PRE" : u"žel","lexem" : u"želja", "SUFF_PRE" : _suffixes_pre_im              , "SUFF_AOR" : _suffixes_aor_h, "SUFF_VA_A" : _suffixes_va_act_o, "lexem_VA_A": "želje", "SUFF_VA_P" : _suffixes_va_pas_n, "lexem_VA_P" : u"želje" }, 
                            u"moći"   : {"lexem_PRE" : "mog" ,"lexem" : u"moga" , "SUFF_PRE" : self._suffixes_pre_morati_jem , "SUFF_AOR" : _suffixes_aor_h, "SUFF_VA_A" : _suffixes_va_act_o, "lexem_VA_A": "moga" , "SUFF_VA_P" : None }, # this is palatalizacija reverted
                            "smjeti"  : {"lexem_PRE" : "smij","lexem" : u"smije", "SUFF_PRE" :_suffixes_pre_em              , "SUFF_AOR" : _suffixes_aor_h, "SUFF_VA_A" : _suffixes_va_act_o, "SUFF_VA_P" : None } # TODO: this is vc - umetanje i - je -> ije (smjeti -> smijem)
                            }
        for word_base, w_dict in _freq_words_data.iteritems():
            word_obj = self.add_word(word_base)

            for v_time in ("PRE","AOR", "VA_A", "VA_P"):
                if w_dict["SUFF_"+v_time]:
                    # if v_time in  ("ACT", "PAS"):
                    #     word_type_conv_str="VA"
                    # else:
                    #     word_type_conv_str=None
                    if ("lexem_%s" % v_time) in w_dict.keys():
                        lexem = w_dict["lexem_%s" % v_time]
                    else:
                        lexem = w_dict["lexem"]
                    word_obj.add_forms(lexem, v_time, w_dict["SUFF_"+v_time]) #, word_type_conv_str=word_type_conv_str)

    def __init_wts(self):
        # self.verbal_adjectives = VerbalAdjectivesType()
        # N", "iz imenica
        for item in self.WORD_BASE_TO_LEXEM_PRE_RULES:
            if len(item)==4:
                is_wb, word_base_item, lexem_spec_item, callback = item
            else:    
                assert len(item)==3, item
                is_wb, word_base_item, lexem_spec_item = item
                callback = None
            word_base_item = uni_revert(to_unicode(word_base_item))

            # if is_wb:
            #     # TODO: check if these should be added as stdwords, check self.__init_stdwords()
            #     assert not callback, "not impl."
            #     assert not isinstance(lexem_spec_item, list)
            #     # dummy, spec_pre = lexem_spec_item
            #     # verb = Verb(word_base_item, ext=spec_pre, status="F", word_type=self)


            # TODO: for each item - add example
            if not isinstance(lexem_spec_item, list):
                lexem_spec_item = [lexem_spec_item]
            lexem_spec_list = []
            for ordnr, spec_item in enumerate(lexem_spec_item):
                params_init = {}
                if is_wb:
                    params_init["status"]="F" # confirmed
                    dummy, spec_pre = spec_item
                else:
                    dummy1, dummy2, spec_pre = spec_item
                params_init["ext_pair"] = (spec_pre, ordnr)
                # NOTE: "wb_check_callback" : callback - should be called in suggest suffix in verb and return no 
                # result
                #params_init = {"ext" : spec_pre} #, "is_wb" : is_wb}
                self._add_wts({}, word_base_item ,  -1, "XX", "", "todo", **params_init)
            # for key, attrs_fix, params_init in self.iter_param_combinations():
            # self._add_wts(attrs_fix, "$BASE$"       ,   -1, key, "", ""  , **params_init)


        # ======== Suffixal verb creation from the book =============
        #
        # self._add_wts({}, "ati"  ,   2, "N", "", "križati")
        # self._add_wts({}, "iti"  ,   2, "N", "", "baštiniti")
        # self._add_wts({}, "ovati",   2, "N", "", "tugovati")
        # self._add_wts({}, "evati",   2, "N", "", "stupnjevati")
        # self._add_wts({}, "irati",   1, "N", "", "telefonirati")
        # # A", "iz pridjeva
        # # NOTE: ima ih 15 a ovi su plodniji
        # self._add_wts({}, "ati"  ,   2, "A", "", "ravnati")
        # self._add_wts({}, "iti"  ,   2, "A", "", "bjeliti")
        # self._add_wts({}, "jeti" ,   2, "A", "", "crnjeti")
        # self._add_wts({}, "ovati",   2, "A", "", "tugovati") # TODO: ovo nije pravi primjer ;)
        # # E", "exclamations", "usklika
        # self._add_wts({}, "čati" ,   -1, "E", "", "mečati")
        # self._add_wts({}, "etati",   -1, "E", "", "meketati")
        # self._add_wts({}, "jati" ,   -1, "E", "", "blejati")
        # self._add_wts({}, "kati" ,   -1, "E", "", "gukati")
        # self._add_wts({}, "otati",   -1, "E", "", "cvokotati")
        # self._add_wts({}, "tati" ,   -1, "E", "", "coktati")
        # # Vp", "od glagola perfektizaija 
        # self._add_wts({}, "nuti" ,   -1, "Vp", "", "kucnuti")
        # # Vi", "imperfektizacija
        # self._add_wts({}, "avati" ,  -1, "Vi", "", "ograničavati")
        # self._add_wts({}, "javati",  -1, "Vi", "", "osposobljavati")
        # self._add_wts({}, "ivati" ,  -1, "Vi", "", "odlučivati")
        # self._add_wts({}, "jivati",  -1, "Vi", "", "navaljivati")

        # TODO: V - prefiksalna tvorba
        # self._add_wts({}, "" ,   -1, "V", "npr. - ")

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
            # ext = getattr(wts, "ext", None)
            #params_init["ext_pair"] = (ordnr, spec_pre)
            ext_pair = getattr(wts, "ext_pair")

            # spec = getattr(wts, "spec", None)
            status = getattr(wts, "status", "T")
            assert status in ("T", "F")
            verb = None
            ext_ch, ext_nr = ext_pair
            try:
                verb = Verb(wts.suff_value, 
                            is_suffix=False if status=="F" else True,
                            ext=ext_ch, status=status) # spec=spec, 
            except BadParamsInitError, e:
                verb = Verb(wts.suff_value, 
                            is_suffix=False if status=="F" else True,
                            ext=ext_nr, status=status) # spec=spec, 
                #if not verb.ext==ext_ch:
                #    import pdb;pdb.set_trace()
                assert verb.ext==ext_ch, "%s!=%s" % (verb.ext, ext_ch)
            for key, form_list in verb:
                for ordnr, form in enumerate(form_list):
                    #                 word_obj , suff_key, suff_value))
                    wts_forms.append((verb, key, ordnr+1, form))
            # NOTE: this call adds list of wts entries into suff.registry
            wts.add_forms(wts_forms) 
        self._wts_forms_initialized = True
        return

    # unicode("čuti", "utf-8")  : (unicode("čuj", "utf-8"), "e"),
    # TODO: pasti -> pasem / padam
    #"jesti"  : ("jed"  , "e"),
    #"plesti" : ("plet" , "e"),
    #"gristi" : ("griz" , "e"),

    # def fun_wc_le_2(word_base):
    #     if count_wparts(word_base)<=2:
    #         return word_base
    #     return None

    def fun_le_4(word_base):
        if len(word_base)<=4:
            return word_base
        return None

    def fun_prijeci(word_base):
        if word_base.endswith(unicode("prijeći", "utf-8")):
            return word_base.replace(unicode("ijeći", "utf-8"), unicode("eći","utf-8"))
        return None

    WORD_BASE_TO_LEXEM_PRE_RULES = [

        # TODO: this is not good - since popasti, prežeti, prokleti, samljeti, prestati (prestanem, prestajem?)
        #       but not ići/ući? should be also done
        # is_wb word_base                   lex_pre  spec_pre
        (True , unicode("žeti", "utf-8")  , (unicode("žanj", "utf-8"), "e")),
        (True , "kleti"                   , ("kun"  , "e") ),
        (True , "mljeti"                  , ("melj" , "e") ),
        (True , "stati"                   , ("stan" , "e") ),
        (True , unicode("ići", "utf-8")   , ("id"   , "e") ),
        (True , unicode("ući", "utf-8")   , (unicode("uđ"  , "utf-8"), "e")),

        # is_wb wb_suffix          lex_pre: cut_from     add  spec_pre
        # TODO: words based on these (čuti, piti, biti, dati) - like prečuti, ispiti, prebiti, predati
        #       have same type of lexem_pre
        #       they are listed down there. find 
        # TODO: currently makes problems: 
        # (False, "iti"                     , (len("ti")    , ""  , "je"), fun_le_4),
        # TODO: currently makes problems: 
        # (False, "ati"                     , (len("ti")    , ""  , "je"), fun_le_4),
        # leti doesn't fit
        #(False, "eti"                     , (len("ti")    , ""  , "je"), fun_le_4),
        # TODO: currently makes problems: 
        # (False, "uti"                     , (len("ti")    , ""  , "je"), fun_le_4),
        # TODO: any more like this?
        (False, "biti"                    ,[(len("iti")   , "" , "i"), 
                                            (len("ti")    , "" , "je")]),
        (False, "piti"                    ,[(len("iti")   , "" , "i"), 
                                            (len("ti")    , "" , "je")]),
        (False, "viti"                    ,[(len("iti")   , "" , "i"), 
                                            (len("ti")    , "" , "je")]),
        (False, "liti"                    ,[(len("iti")   , "" , "i"), 
                                            (len("ti")    , "" , "je")]),
        (False, "siti"                    ,[(len("iti")   , "" , "i"), 
                                            (len("ti")    , "" , "je")]),
        # TODO: glodati - is some exception - glodjem 
        (False, "pasti"                   , [(len("sti")  , "d" , "a"),
                                             (len("ti")   , ""  , "e")]),
        (False, unicode("lodati", "utf-8"), (len("ati")   , ""  , "je")),
        (False, unicode("ždati", "utf-8") , (len("ati")   , ""  , "i")),
        (False, "dati"                    ,[(len("ati")   , "" , "a"), 
                                            (len("ti")    , "" , "je")]),
        (False, unicode("čuti", "utf-8")  , (len("ti")    , "" , "je")),

        (False, "krasti"                  , (len("sti"),   "d" , "e")),
        (False, "rasti"                   , (len("i")  ,   ""  , "e")),
        (False, "pasti"                   , (len("sti"),   "d" , "a")),
        (False, "asti"                    , (len("sti"),   "t" , "e")),
        (False, "lesti"                   , (len("sti"),   "t" , "e")),
        (False, "mesti"                   , (len("sti"),   "t" , "e")),
        (False, "nesti"                   , (len("sti"),   "s" , "e")),
        (False, "tresti"                  , (len("sti"),   "s" , "e")),
        (False, "sresti"                  , (len("sti"),   "tn", "e")),
        (False, "sjesti"                  , (len("sti"),   "dn", "e")),
        (False, "vesti"                   , [(len("sti"),   "d" , "e"), (len("esti"),  "ez", "e")]),
        (False, "esti"                    , (len("sti"),   "d" , "e")),
        (False, "isti"                    , (len("sti"),   "z" , "e")),
        (False, "sti"                     , (len("sti"),   ""  , "e")),
        (False, "nijeti"                  , (len("eti"),   ""  , "e")),
        (False, "rijeti"                  , (len("ijeti"), ""  , "e")),
        (False, "mjeti"                   , (len("mjeti"), "mij","e")),
        (False, "zvati"                   , (len("zvati"), "zov","e")),
        (False, "ojevati"                 , (len("evati"), "uj", "e")),
        (False, LJ+"evati"                , (len("evati"), "uj", "e")),
        (False, NJ+"evati"                , (len("evati"), "uj", "e")),
        (False, unicode("čevati", "utf-8"), (len("evati"), "uj", "e")),
        (False, unicode("ševati", "utf-8"), (len("evati"), "uj", "e")),
        (False, unicode("đevati", "utf-8"), (len("evati"), "uj", "e")),
        (False, unicode("ćevati", "utf-8"), (len("evati"), "uj", "e")),
        (False, unicode("ževati", "utf-8"), (len("evati"), "uj", "e")),
        (False, "evati"                   , (len("ati")  , ""  , "a")),
        (False, "ivati"                   , [(len("ivati"),"uj", "e"), (len("ati")  ,""  , "a"),]),
        # NOTE: it seems that this is not needed: "ovati": word_base.replace(u"ije", u"je")
        (False, "ovati"                   , (len("ovati") ,"uj", "e")),
        (False, LJ+"eti"                  , (len("leti") , "l" , "i")),
        (False, NJ+"eti"                  , (len("neti") , "n" , "i")),
        (False, "jeti"                    , (len("jeti") , ""  , "i")),
        (False, "vati"                    , [(len("ati") , ""  , "a"), (len("vati"), "j" , "e")]),
        (False, unicode("peti", "utf-8")  , (len("eti")  , "n" , "e")),
        (False, unicode("četi", "utf-8")  , (len("eti")  , "n" , "e")),
        (False, unicode("teti", "utf-8")  , (len("eti")  , "m" , "e")),
        (False, unicode("zeti", "utf-8")  , (len("eti")  , "m" , "e")),
        (False, unicode("žeti", "utf-8")  , (len("eti")  , "m" , "e")),
        # TODO: check this later - was duplicated
        # (False, unicode("teti", "utf-8")  , (len("eti")  , "n" , "e")),
        (False, "drhtati"                 , [(len("ati") , ""  , "je"), (len("ati") , ""  , "i" )]),
        (False, "prati"                   , (len("rati") , "er"  , "e")),
        # TODO: j+e -> ""+"je"
        (False, "stati"                   , [(len("ti")  , "j" , "e" ), (len("ati") , ""  , "a")]),
        # nastojati -> nastojim, brijati -> brijem
        (False, "jati"                    , [(len("ati") , ""  , "i" ), (len("ati") , ""  , "e")]),
        # "ati"
        (False, unicode("ištati", "utf-8"), (len("ati")   , ""  , "i")),
        (False, unicode("štati" , "utf-8"), (len("ati")   , ""  , "a")),
        # čati, žati, šati, jati : cičati -> cičam , cičiti -> cičim
        # NOTE: for some [iu]čati or [r]šati is a, for some is i
        #       cičati -> cičim, pričati -> pričam, čučati -> čučim
        #       stršati -> stršim, pogoršati -> pogoršam
        (False, unicode("ičati", "utf-8") , [(len("ati"), "", "i"), (len("ati"), "", "a")]),
        (False, unicode("učati", "utf-8") , [(len("ati"), "", "i"), (len("ati"), "", "a")]),
        (False, unicode("ršati", "utf-8") , [(len("ati"), "", "i"), (len("ati"), "", "a")]),
        # NOTE: it seems that rest čati is "a" - book says i? - 143 p., 285 t.
        (False, unicode("čati" , "utf-8") , (len("ati")   , ""  , "a")),
        (False, unicode("šati" , "utf-8") , (len("ati")   , ""  , "a")),
        (False, unicode("ržati", "utf-8") , (len("ati")   , ""  , "i")),
        (False, unicode("žati" , "utf-8") , (len("ati")   , ""  , "a")),
        (False, unicode("jati" , "utf-8") , (len("ati")   , ""  , "i")),
        # NOTE: duplicate (False, unicode("stati", "utf-8") , (len("ati")   , ""  , "i")),
        (False, unicode("tragati","utf-8"), (len("gati")  , unicode("ž", "utf-8"), "i")),
        ]
    # TODO: maybe there can be a rule to distinct them
    # multiple result - skakati -> skačem, čekati -> čekam
    for ch in WordSuffixes.VC_J_CHARLIST_FROM:
        WORD_BASE_TO_LEXEM_PRE_RULES.append((False, ch+"ati", [(len(u"ati"), "", "a"), (len(u"ati"), "", "je")]))

            
            
    WORD_BASE_TO_LEXEM_PRE_RULES += [
        (False, "ati"                     , [(len("ati"), "", "e"), (len("ati"), "", "a")]),
        # TODO: len(word_base)<=4
        (False, "suti"                    , (len("suti")  , "sp", "e")),
        (False, "uti"                     , (len("uti")   , ""  , "e")),
        (False, "eti"                     , (len("eti")   , ""  , "e")),
        (False, "iti"                     , (len("iti")   , ""  , "i")),
        # default rule - e is most common
        # TODO: assert lexem_spec_list[0][-1] not in AEIOU, "shoudn't happen"
        (False, "ti"                      , (len("ti" )   , ""  , "e")), 
        # TODO: čžšđć + e -> tkhgzs + je
        # NOTE: prijeći - word_base will be by callback replaced ije->e
        (False, unicode("prijeći","utf-8"), (len(u"ci"), unicode("đ", "utf-8"), "e"), fun_prijeci),
        (False, unicode("naći", "utf-8"), (len(u"ci"), unicode("đ", "utf-8"), "e")),
        (False, unicode("zaći", "utf-8"), (len(u"ci"), unicode("đ", "utf-8"), "e")),
        (False, unicode("oći" , "utf-8"), (len(u"ci"), unicode("đ", "utf-8"), "e")), # or doći
        (False, unicode("ići" , "utf-8"), (len(u"ci"), unicode("ž", "utf-8"), "e")),
        # TODO: not natural? e.g.: vrći, odvrći
        (False, unicode("rći" , "utf-8"), (len(u"ci"), unicode("ž", "utf-8"), "e")),
        (False, unicode("aći" , "utf-8"), (len(u"ci"), unicode("č", "utf-8"), "e")),
        (False, unicode("ući" , "utf-8"), (len(u"ci"), unicode("č", "utf-8"), "e")),
        # multi result
        # from ć -> ž, č (or đ)
        # gn -> ž
        #     pobjeći -> pobježem (pobjegnem)
        #     leći    -> ležem    (legnuti)
        #     priseći -> prisežem (prisegnuti)
        #     moći    -> možem    (mognuti)
        #     smoći   -> smožem   (smognuti)
        #     odmoći  -> odmožem  (iako odmagati -> odmažem)

        # put in exceptions 
        #     gn+j -> đ
        #     prijeći -> prijeđem (prijegnuti -> pregjem)
        #     doći    -> dođem    (dognuti -> dogjem)

        # kn -> č
        #     isjeći  -> isječem  (isjeknuti)
        #     peći    -> pečem    (peknuti) 
        #     steći   -> stečem   (steknuti)
        #     izreći  -> rečem    (reknuti)
        #     priteći -> pritečem (priteknuti)
        #     presjeći-> presječem(presjeknuti)
        #     odmaći  -> odmačem  (odmaknuti)
        (False, unicode("ći", "utf-8"), [(len("ci"), unicode("k", "utf-8"), "je"), 
                                         (len("ci"), unicode("g", "utf-8"), "je"),
                                         # TODO: is this also an option?
                                         # (len("ci"), unicode("kn", "utf-8"), "e"), 
                                         # (len("ci"), unicode("gn", "utf-8"), "e"),
                                         ]),
        ]

    # CHECK RULES
    for item in WORD_BASE_TO_LEXEM_PRE_RULES:
        is_wb, word_base_item, lexem_spec_item = item[:3]
        if not is_wb:
            if not isinstance(lexem_spec_item, list):
                lexem_spec_item = [lexem_spec_item]
            all_spec_pre = {}
            for cut_from, add_suffix, spec_pre in lexem_spec_item:
                # exception
                if not word_base_item in ("vesti", unicode("ći", "utf-8")):
                    assert not spec_pre in all_spec_pre, item
                    all_spec_pre[spec_pre]=True
                assert cut_from<=len(word_base_item)

    @classmethod
    def suggest_lexem(cls, word_base_orig, is_suffix=False, match_multi_rules=True):
        # TODO: from this you can get present suffix type (em, jem, ...)
        # TODO: this should be Verb. or verb. method?
        word_base_orig = to_unicode(word_base_orig)
        if not word_base_orig[-2:] in ("ti", unicode("ći", "utf-8")):
            raise Exception("%s doesn't end in (ti/chi)" % repr(word_base_orig))
        #assert word_base_orig[-2:] in ("ti", unicode("ći", "utf-8")), # must be infinitive

        word_base = uni_prepare(word_base_orig)
        if is_suffix:
            match_multi_rules=False

        assert "lj" not in word_base
        assert "nj" not in word_base

        # TODO: make more general - ije->je/e/i done on several places
        # if word_base.endswith(unicode("ijeći","utf-8")):
        #     word_base = word_base.replace(unicode("ijeći", "utf-8"), unicode("eći","utf-8"))

        if not is_suffix:
            assert len(word_base)>2, repr(word_base)

        lexem_spec_list = []
        for item in cls.WORD_BASE_TO_LEXEM_PRE_RULES:
            if len(item)==4:
                is_wb, word_base_item_orig, lexem_spec_item, callback = item
            else:    
                assert len(item)==3, item
                is_wb, word_base_item_orig, lexem_spec_item = item
                callback = None
            word_base_item = uni_prepare(word_base_item_orig)
            if is_wb:
                if not is_suffix and word_base==word_base_item:
                    assert not callback, "not impl."
                    lexem_spec_list = tuple(list(lexem_spec_item)+[None])
                    break
            else:
                if is_suffix:
                    matched = (word_base==word_base_item)
                else:
                    matched = (word_base.endswith(word_base_item))
                if matched:
                    if callback:
                        word_base_new = callback(word_base)
                        if not word_base_new:
                            continue
                        #not is_suffix 
                        word_base = word_base_new
                    if not isinstance(lexem_spec_item, list):
                        lexem_spec_item = [lexem_spec_item]
                    # lexem_spec_list = []
                    for cut_from, add_suffix, spec_pre in lexem_spec_item:
                        # TODO: make more general - check for words in db (is this enough, is there opsti)
                        #       put in rule as remove_vc_list or just list htme
                        if word_base.endswith("epsti") or word_base.endswith("upsti") :
                            word_base_1, word_base_2 = word_base[:-len(word_base_item)], word_base_item[-len(word_base_item):]
                            word_base_1, word_base_2 = WordSuffixes.remove_vc_Z(word_base_1, word_base_2, trace_vc_list=None)
                            word_base = uni_prepare(word_base_1+word_base_2)
                        lexem_pre = word_base[:-cut_from]+add_suffix
                        lexem_rule = (cut_from, add_suffix)
                        lexem_spec_list.append((lexem_pre, spec_pre, lexem_rule))
                    assert lexem_spec_list
                    #cut_from, add_suffix, spec_pre = lexem_spec_item
                    #lexem_spec_list = word_base[:-cut_from]+add_suffix, spec_pre
                    if is_suffix and callback:
                        # NOTE: for fun_prijeci this shouldn't be done - exception
                        # TODO: if there will be more callbacks - then do some way general 
                        #       callback should return something
                        if match_multi_rules and callback.__name__ not in ("fun_prijeci",):
                            # maybe there are more
                            continue
                    break
        assert lexem_spec_list, "internal error: for word_base %s lexem_pre not found" % (repr(word_base),)
        if not isinstance(lexem_spec_list, list):
            lexem_spec_list = [lexem_spec_list]
        # TODO: not needed? 
        #       lexem, suffix = WordSuffixes.remove_vc_S(lexem, suffix)
        result = []
        for lexem, spec, lexem_rule in lexem_spec_list:
            # TODO: make more general 
            lexem, spec = WordSuffixes.remove_vc_Z(lexem, spec, trace_vc_list=None)
            lexem = uni_revert(lexem)
            if word_base[-2:] in "ti":
                lexem_inf = uni_revert(word_base_orig[:-2])
            else:
                assert word_base[-2:]==u"ći"
                lexem_inf = lexem
            result.append((lexem, spec, lexem_inf, lexem_rule))
        return result

    # def iter_suffix_cross_table(self):
    #     """ returns 
    #     >>> l = [(iter2.time,iter2.suf_id, iter2.suffix.name) for iter2 in VERBS.iter_suffix_cross_table()]
    #     >>> len(l)
    #     11
    #     >>> l[0]
    #     ('PRE', '1', u'V#PRE#-em')
    #     >>> l[-1]
    #     ('IMV', '2', u'V#IMV#-i')
    #     """
    #     suffix_dict = self.get_suffix_time_dict()
    #     for time in base.ATTR_TIME.values:
    #         suffix_list = suffix_dict[time]
    #         suf_id_list = sorted(suffix_list.keys())
    #         for suf_id in suf_id_list:
    #             suffix = suffix_list[suf_id]
    #             yield IterAttrs(self, suffix, suf_id=suf_id, add_gender=False,
    #                             iter_attrs=[base.ATTR_NUMBER, base.ATTR_PERSON],
    #                             time=time)
    #
    # def get_suffix_time_dict(self):
    #     if not getattr(self, "suffix_time_dict", None):
    #         self.suffix_time_dict = dict([(time, {}) for time in base.ATTR_TIME.values])
    #         for name4detect, suffixes in self.suffixes4detection.iteritems():
    #             # TODO: i know i know, not nice, but i have deadlines ;)
    #             time,suf_id = name4detect.split("#")
    #             # NOTE: from suffixes.name = 'V#AOR#-oh' -> get AOR as Aorist
    #             assert time==suffixes.name.split("#")[1]
    #             if time not in self.suffix_time_dict:
    #                 raise Exception("Nouns: %s not in %s (name=%s)" % (time, self.suffix_time_dict.keys(), name))
    #             assert suf_id not in self.suffix_time_dict[time]
    #             self.suffix_time_dict[time][suf_id] = suffixes
    #     return self.suffix_time_dict


if not base.is_word_type_registred("V"):
    VERBS             = VerbType()
    # NOTE: this looks and sounds like monkey patching - don't like this but :(
    # TODO: this code is copied and adjusted from nouns, so make it DRY
    # VERBAL_ADJECTIVES = VERBS.verbal_adjectives
# ----------------------------------------------------------
else:
# ----------------------------------------------------------
    VERBS = base.get_word_type("V")
    # VERBAL_ADJECTIVES = base.get_word_type("VA")

WORD_TYPE = VERBS
WORDS     = WORD_TYPE.std_words

def test():
    print "%s: running doctests" % __name__
    import doctest
    doctest.testmod()
    base.run_doctests(( "test_verbs_type.txt",
                        "test_verbs_base_pre.txt",
                        "test_verbs-PRE.txt",
                        "test_verbs-AOR-IMP.txt", 
                        "test_verbs_ad.txt", 
                        "test_verbs_freq.txt",
                        "test_verbs_book.txt",
                     ))

if __name__ == "__main__":
    test()

