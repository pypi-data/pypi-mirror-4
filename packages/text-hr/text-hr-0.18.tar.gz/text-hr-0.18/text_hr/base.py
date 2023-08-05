# coding=utf-8
# type of words
# doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
"""
"""
import os, codecs, doctest, pprint

from text_hr.utils import iter_mine
from text_hr.utils import to_unicode

_WS_ALL = set()
_ATTR_LIST = {}
_TYPE_LIST = {}

STATUS_CHOICES = (
                    ("T","Processed, suggested as unconfirmed"),
                    ("F","Processed, suggested as confirmed"),
                    ("U", "Unprocessed/unverified"),
                    ("C", "Confirmed"),
                    ("R", "Rejected"),
                    ("D", "Duplicate candidate (still active)"),

                    #("I", "Ignored"),
                    #("S", "Suspicious"),
                    # TODO: think about how to detect similar word_obj-s (word_base)
                 )
STATUS_LIST = tuple([s for s, d in STATUS_CHOICES])

def is_word_type_registred(code):
    return _TYPE_LIST.has_key(code)

def get_word_type(code):
    return _TYPE_LIST[code]
# ---------------------------------------- 


class WordAttr(object):
    def __init__(self, code, can_fix, can_ch, name, values):
        # TODO: each value should have some description
        self.code, self.name, self.values = code, name, values
        self.can_fix, self.can_ch = can_fix, can_ch
        assert self.can_fix or self.can_ch, "must be fix attr, change attr or both (%s)" % self
        assert code not in _ATTR_LIST
        _ATTR_LIST[code]=self

    def __str__(self):
        return "%-3s %s (%d)" % (self.code, self.name, len(self.values))
    def __repr__(self):
        return "%s at %X" % (str(self), id(self))

# TODO: each attr should have order - and all wtypes should define attrs in correct order
#                                    can_fix can_ch
ATTR_GENDER      = WordAttr("GEN"  , True , True , "Rod", ("M", "F", "N")) # male, female, neutral
ATTR_NUMBER      = WordAttr("NUM"  , True , True , "Broj", ("S", "P")) #singular/plural
ATTR_DECLINATION = WordAttr("DEC"  , False, True , "Padez (deklinacija)", ("N","G","D","A","V","L","I")) #Nominativ/genitiv/...
# TODO: distinct 3 from 3M/3F/3N
ATTR_PERSON      = WordAttr("PER"  , True , True , "Osoba", ("1","2","3")) # me, you, he/she/it ...
ATTR_PERSON_MFN  = WordAttr("PER_MFN",True, True , "Osoba-1/2/3MFN", ("1","2","3M", "3F", "3N")) # me, you, he,she,it ...
ATTR_PERSON_3MFN = WordAttr("PER_3MFN",True,True , "Osoba-3MFN"    , ("3M", "3F", "3N")) # he,she,it ...
ATTR_COMPARATION = WordAttr("GRD"  , False, True , "Stupnjevanje", ("P_N","P_O","COM","SUP")) #Positive/comparative/superlative
ATTR_TIME        = WordAttr("TIM"  , False, True , "Vrijeme", ("PRE","AOR","IMP", "IMV", "VA_A", "VA_P",)) # present, aorist, imperfekt, imperativ
# NOTE: prebačen u ATTR_TIME
#ATTR_VA_TYPE     = WordAttr("WAY"  , False, True , "Glagolski pridjev radni i trpni", ("ACT","PAS")) # aktiv i pasiv (radni i trpni)
#ATTR_ADJ_TYPE    = WordAttr("ADJ_T", False, True , "Vrste pridjeva", ["NEO", "ODR"]) # neodređeni / određeni
ATTR_NUM_TYPE    = WordAttr("NTY"  , True , False, "Vrsta broja", ("MAI","ORD")) #Main / order number
ATTR_ADV_TYPE    = WordAttr("ADV_T", True , False, "Vrste priloga", []) # types will be defined later
ATTR_PREP_TYPE   = WordAttr("PREP_T", True , False, "Vrste prijedloga, prepositions", []) # types will be defined later
ATTR_CONJ_TYPE   = WordAttr("CONJ_T", True , False, "Vrste veznika (conjuctions)", []) # types will be defined later
ATTR_EXCL_TYPE   = WordAttr("EXCL_T", True , False, "Vrste usklika (exclamations)", []) # types will be defined later
# TODO: uloga u rečenici imenične i pridjevne - postoji mapiranje između vrste zamjenice i ovoga
# ATTR_PRON_RU_TYPE    = WordAttr("PRON_T", "Uloga zamjenice u rečenici", ("IME", "PRI")) 
ATTR_PRON_TYPE   = WordAttr("PRON_T", True , False, "Vrste zamjenica (pronouns)", ("OSO", "POV", "POS", "PPO", "POK", "UPI", 
                                 "UOD.IME", "NEO")) # osobne, povratne, posvojne, povratno-posvojne, pokazne, 
                                 # upitne, odnosne, neodređene
# ATTR_N_SUFF      = WordAttr("N_SUFF"  , True , False , "Noun suffix type", ("A.M0", "N")) # Sklonidba M nominativ suffix 0, ...

# ---------------------------------------- 

# TODO: need to distinguish changeable and not changeable word types - URGENTLY - TOO MUCH ASSERTS
# class WordTypeBase, WordTypeChangeable, WordTypeFixed
class WordTypeBase(object):

    def __init__(self, code, name, attrs_fix=(), attrs_ch=(), 
                 allow_duplicate_words=False, register_it=True):
        assert code not in _TYPE_LIST.keys(), "%s, %s" % (code, _TYPE_LIST.keys())
        self.allow_duplicate_words, self.registred = allow_duplicate_words, register_it
        self.code, self.name  = code, name
        self.attrs_fix      = list(attrs_fix)
        self.attrs_ch       = list(attrs_ch)
        set_fix = set(self.attrs_fix)
        assert len(set_fix)==len(self.attrs_fix), "%s have some duplicates fix attrs %s" % (code, self.attr_fix)
        set_ch  = set(self.attrs_ch) 
        assert len(set_ch)==len(self.attrs_ch), "%s have some duplicates fix attrs %s" % (code, self.attr_ch)
        intersection = set_fix.intersection(set_ch)
        if code not in ("PRON.OSO","PRON.POS"): 
            assert not intersection, "%s have some attrs in fix and ch too - %s" % (code, intersection)
        for attr in self.attrs_fix:
            assert attr.can_fix, "%s has '%s' - should be fixable" % (self.name, attr.name)
        for attr in self.attrs_ch:
            assert attr.can_ch, "%s has '%s' - should be changeable" % (self.name, attr.name)
        self.is_changeable = (self.attrs_ch and True or False)

        # NOTE: order is preserved
        self.attrs = self.attrs_fix +  self.attrs_ch
        if self.registred:
            _TYPE_LIST[code]       = self

        self.wts_list = {}


    def unregister(self):
        #assert self.registred
        if _TYPE_LIST and self.code in _TYPE_LIST.keys():
            del _TYPE_LIST[self.code]

    # because Adverbs have some too - this moved from Changeable to here
    def _add_wts(self, attrs_fix, suff_value, freq_type, group, desc="", 
                 examples="", vc_list=None, suffixes=None, base_ends_aeiou=None, **kwargs):
        # TODO: check if this is ok
        if False:
            from morphs import WordTypeSuffix
            # TODO: suffixes
            wts = WordTypeSuffix(word_type=self, attrs_fix=attrs_fix, 
                                 suff_value=suff_value, freq_type=freq_type, 
                                 group=group, desc=desc, examples=examples, vc_list=vc_list, 
                                 base_ends_aeiou=base_ends_aeiou,
                                 **kwargs)
            key = wts.code
            assert key not in self.wts_list, "%s found duplicated" % key
            self.wts_list[key] = wts
        else:
            # TODO: all should be unicode
            if isinstance(suff_value, unicode):
                key = "|".join([unicode(s) for s in (attrs_fix, suff_value, vc_list, base_ends_aeiou, kwargs)])
            else:
                key = "|".join([str(s) for s in (attrs_fix, suff_value, vc_list, base_ends_aeiou, kwargs)])
            # should be max: freq_type=freq_type
            # should be from max: group=group 
            # ignore: desc=desc 
            # ignore: examples=examples

            if key in self.wts_list:
                # NOTE: not adding same but other semantics, 
                #       will improve performance a bit
                # print "%s found duplicated, ignored" % wts.code
                pass
            else:
                from morphs import WordTypeSuffix
                wts = WordTypeSuffix(word_type=self, attrs_fix=attrs_fix, 
                                     suff_value=suff_value, freq_type=freq_type, 
                                     group=group, desc=desc, examples=examples, vc_list=vc_list, 
                                     base_ends_aeiou=base_ends_aeiou,
                                     **kwargs)
                self.wts_list[key] = wts
                
    # NOTE: This couldn't work while del is not called while it is in _TYPE_LIST
    # def __del__(self):
    #     #import pdb; pdb.set_trace()
    #     self.unregister()
        
    def __str__(self):
        return "%-3s %s (%s/%s)" % (self.code, self.name, self.attrs_fix, self.attrs_ch)

    def __repr__(self):
        return "%s at %X" % (str(self), id(self))

# ---------------------------------------- 

class FixedWordType(WordTypeBase):

    def __init__(self, code, name, attrs_fix=(), allow_duplicate_words=False,
                 register_it=True):
        super(FixedWordType, self).__init__(code, name, attrs_fix=attrs_fix, 
              attrs_ch=(), allow_duplicate_words=allow_duplicate_words,
              register_it=register_it)
        assert not self.is_changeable
        if self.attrs_fix:
            # NOTE: This is because WordSet works like this, but no need to improve it currently
            assert len(self.attrs_fix)==1, "currently for fix words 0/1 fix attrs supported"
            attr_to_update_values = self.attrs_fix[0]
        else:
            attr_to_update_values = None
        self.std_words = FixedWordList(self.code, attr_to_update_values=attr_to_update_values,
                                       allow_duplicates = self.allow_duplicate_words)

# ---------------------------------------- 

# TODO: move this to morphs.py
class ChangeableWordType(WordTypeBase):

    SUFF_TYPES = { "SINGLE" : "suffix used only for single word",
                   "SOME"   : "suffix used for some small amount of words (<20)",
                   "MANY"   : "suffix used for many words (>20), used in word type detection"
                 }

    @classmethod
    def iter_param_combinations(cls):
        raise NotImplementedError("shoud be impl. in child class")

    def __init__(self, code, name, attrs_fix=(), attrs_ch=(), 
                 allow_duplicate_words=False, register_it=True):
        super(ChangeableWordType, self).__init__(code, name, attrs_fix=attrs_fix, 
                    attrs_ch=attrs_ch, allow_duplicate_words = allow_duplicate_words,
                    register_it=register_it)
        assert self.is_changeable
        self.suffixes_dict = {}
        self.suffixes4detection = {} # TODO: only for MANY types
        # standard words - for changeable is 
        # if self.code in ("VA",):
        # self.std_words = None # TODO: not solved good, belong to V wordtype
        # else:
        # dictionary of ChangeableWord
        self.std_words = {}

        self._wts_forms_initialized = False
        self._SUFFIX_TEMPL = {}
        self.PARAMS_ADD = {}

    def std_words_forms(self, stdword):
        out = []
        if isinstance(self.std_words[stdword], (list, tuple)):
            chword_old_list = self.std_words[stdword]
        else:
            chword_old_list = [self.std_words[stdword]]
        for chword_old in chword_old_list:
            for k1,v1 in chword_old.get_all_forms():
                if isinstance(v1, basestring):
                    out.append((k1,v1))
                else:
                    for k,v in v1.forms_ordered:
                        out.append(("%s/%s" % (k1,k),v))
        return out


    # TODO: some of those are general and need to go to morphs.py. once ...
    def get_text(self, suff_code, vars_in):
        templ = self._SUFFIX_TEMPL[suff_code]
        return self._get_text(templ, suff_code, vars_in)

    def _get_text(self, templ, suff_code, vars_in, check_vals=True):
        vars_use = vars_in.copy()
        for k,v in vars_in.iteritems():
            # if not k in self.PARAMS_ADD[suff_code]:
            #     import pdb;pdb.set_trace() 
            if check_vals:
                assert k in self.PARAMS_ADD[suff_code], k
                vals = self.PARAMS_ADD[suff_code][k]
                if isinstance(vals, dict):
                    # import pdb;pdb.set_trace() 
                    found_v2 = None
                    if isinstance(v, int):
                        v = sorted(vals.keys())[v]
                        found_v2 = vals[v]
                        vars_use[k]=v[3:]
                    else:
                        for k2, v2 in vals.iteritems():
                            # 01234
                            # 01_something
                            assert k2[2]=="_"
                            if k2[3:]==v:
                                found_v2 = v2
                                break
                    if found_v2:
                        for k3,v3 in found_v2.iteritems():
                            assert k3 not in vars_use
                            vars_use[k3]=v3
                    assert check_vals
                    assert found_v2, "%s not in ord.dict %s" % (v, vals)
                else:
                    if isinstance(v, int):
                        v = self.PARAMS_ADD[suff_code][k][v]
                        vars_use[k]=v
                    else:
                        if check_vals:
                            assert v in self.PARAMS_ADD[suff_code][k], v
            else:
                assert not isinstance(v, int)

            if "%(" in v:
                vars_use[k]=v % vars_use

        if "ext" in self.PARAMS_ADD[suff_code] and not "ext" in vars_use:
            vals = self.PARAMS_ADD[suff_code]["ext"]
            if isinstance(vals, dict):
                # import pdb;pdb.set_trace() 
                assert False
                ext_default = sorted(vals.keys())[0][3:]
            else:
                ext_default = vals[0]
            vars_use["ext"]=ext_default

        return templ % vars_use

    # TODO: rename
    def get_all(self, suff_code):
        ext_list_dict = None
        if ("ext" in self.PARAMS_ADD[suff_code]):
            ext_list = self.PARAMS_ADD[suff_code]["ext"]
            if isinstance(ext_list, dict):
                ext_list_dict = ext_list
                ext_list = self._get_ext_list(self.PARAMS_ADD[suff_code]["ext"])
        else:
            ext_list = None
            
        all_vars = {}
        for k,v_list in self.PARAMS_ADD[suff_code].iteritems():
            if k=="ext":
                continue
            all_vals = []
            for val in v_list:
                # TODO: what if something else is like ext.dict as in verbs - not done!
                for suff in val.split("|"):
                    if suff not in all_vals:
                        if "%(ext)s" in suff:
                            assert ext_list
                            assert not isinstance(ext_list, dict), "not impl. for this case"
                            suff = "|".join([suff % {"ext" : ext} for ext in ext_list])
                        all_vals.append(suff)
            all_vars[k] = "|".join(all_vals)
            
        if ext_list:
            if ext_list_dict:
                extra_vars = {"ext" : []}
                for k2 in sorted(ext_list_dict.keys()):
                    v2 = ext_list_dict[k2]
                    extra_vars["ext"].append(k2[3:])
                    for k3, v3 in v2.iteritems():
                        if k3 not in extra_vars:
                            extra_vars[k3]=[]
                        extra_vars[k3].append(v3)
                for k3,v3_list in extra_vars.iteritems():
                    assert k3 not in all_vars, "not possible for now"
                    all_vars[k3] = "|".join(v3_list)

            templ = []
            for line in self._SUFFIX_TEMPL[suff_code].split("\n"):
                line = line.rstrip("\n")
                if "%(ext)s" in line:
                    s_list = line.split() 
                    assert len(s_list)==2
                    suff = s_list[1]
                    suff_new = []
                    for suff_item in suff.split("|"):
                        for s_item in [suff_item.replace("%(ext)s", ext) for ext in ext_list]:
                            if s_item not in suff_new:
                                suff_new.append(s_item)
                    suff_new = "|".join(suff_new)
                    line = "        %s %s" % (s_list[0], suff_new)
                templ.append(line)
            templ = "\n".join(templ)
        else:
            templ = self._SUFFIX_TEMPL[suff_code]
        # print templ, all_vars
        result = self._get_text(templ, suff_code, all_vars, False)
        return result

    
    @staticmethod
    def _get_ext_list(ext_list):
        if isinstance(ext_list, dict):
            # 01234 
            # 01_je
            ext_list_new = []
            for e in sorted(ext_list.keys()):
                assert e[2]=="_"
                ext_list_new.append(e[3:])
            ext_list = ext_list_new
        #elif not isinstance(ext_list, (tuple, list)):
        #    ext_list = [ext_list]
        return ext_list

    def _add_suffixes(self, suff_code):
        iter_base = []
        iter_keys = []

        #code_fix, code_rest, call_get_all, attrs_ch = self. _get_add_suffix_params(suff_code)
        #def _get_add_suffix_params(self, suff_code):
        if self.code=="N":
            # 01234
            # A-Moe
            code_fix  = suff_code[2].upper() # gender
            code_rest = (suff_code[0].upper()+suff_code[3:].lower())
            attrs_ch = self.attrs_ch
            call_get_all = True
        elif self.code=="V":
            code_fix = ""
            code_rest = suff_code
            if suff_code.startswith("VA_"):
                # NOTE: VA has GENDER
                attrs_ch = (ATTR_NUMBER, ATTR_GENDER)
            else:
                attrs_ch = (ATTR_NUMBER, ATTR_PERSON)
            call_get_all = True
        else:
            raise NotImplementedError("for %s not implemented" % self.code)
        params_norm = self.PARAMS_ADD[suff_code].copy()
        if "ext" in params_norm:
            ext_list = self._get_ext_list(params_norm.pop("ext"))
        else:
            ext_list = [""]

        params_keys = sorted(params_norm.keys())
        for k in params_keys:
            v_list = params_norm[k]
            assert not k=="ext"
            iter_keys.append(k)
            iter_base.append(len(v_list))

        ordnr = 0
        for ext in ext_list:
            for val in iter_mine(*iter_base):
                ordnr+=1
                val_spec="/".join([str(v) for v in val])
                name = "%s/%s/%s" % (suff_code, ext, val_spec)
                code = "%s#%s%d" % (code_fix, code_rest, ordnr)
                params = dict([(iter_keys[j],v) for j, v in enumerate(val)])
                # TODO: what in case like in verbs is ext, when value_list is ordered dict and not list?
                params["ext"]=ext
                #(ATTR_NUMBER, ATTR_DECLINATION)
                suff = self.add_suffixes("", "MANY", name, code, 
                                         attrs_ch,
                                         self.get_text(suff_code, params))
                # print name, code, suff
        # if call_get_all:
        # self._add_suffixes_all(suff_code)
        # def _add_suffixes_all(self, suff_code):
        # code_fix, code_rest, call_get_all, attrs_ch = self._get_add_suffix_params(suff_code)
        assert call_get_all
        name = "%s/%s/%s" % (suff_code, "*", "*")
        code = "%s#%s%s" % (code_fix, code_rest, "*")
        self.add_suffixes("", "MANY", name, code, 
                          attrs_ch, # (ATTR_NUMBER, ATTR_DECLINATION),
                          self.get_all(suff_code))

    def adjust_key(self, key, keys_to_search):
        """
        Testing register/unregister too:
        >>> bef = _TYPE_LIST.keys()
        >>> wt = ChangeableWordType("X", "dummy", attrs_ch=[ATTR_TIME], 
        ...                        register_it=False)
        >>> bef==_TYPE_LIST.keys()
        True
        >>> wt.adjust_key("xx", [u"X#xx#zzz", u"X#xx#yyy"])
        u'X#xx#'
        >>> wt.adjust_key("X#xx", [u"X#xx#zzz", u"X#xx#yyy"])
        u'X#xx#'
        >>> wt.adjust_key("xx#uu", [u"X#xx#zzz", u"X#xx#yyy"])
        u'X#xx#uu'

        If only one is like then return this one:
        >>> wt.adjust_key("xx", [u"X#xx#yy", u"X#yy#zzz"])
        u'X#xx#yy'
        >>> wt.adjust_key("xx#u", [u"X#xx#uuu", u"X#xx#yyy"])
        u'X#xx#uuu'

        This doesn't influence when it is not registred, but anyway:
        >>> wt.unregister()
        >>> bef==_TYPE_LIST.keys()
        True
        
        Don't know how to solve this properly, this tests leave this module registred in wtypes.py when testing:
        """
        if key.count("#")!=2:
            if not key.startswith(self.code+"#"):
                key="%s#%s" % (self.code, key)
            if key.count("#")!=2:
                key+="#"
            assert key.count("#")==2, key
        key = to_unicode(key)
        if key not in keys_to_search:
            keys_like = [k for k in keys_to_search if k.startswith(key)]
            if len(keys_like)==1:
                key = keys_like[0]
            # else:
            #     import pdb;pdb.set_trace()
        return key

    def add_word(self, word_base, attrs_fix=()):
        # TODO: use new ChangeableWord classes
        from morphs import ChangeableWordOld
        word = ChangeableWordOld(self.code, word_base, attrs_fix)
        word_base = to_unicode(word_base)
        if word_base in self.std_words.keys():
            if self.allow_duplicate_words:
                #import pdb; pdb.set_trace()
                old_val = self.std_words[word_base]
                if isinstance(old_val, list):
                    self.std_words[word_base].append(word)
                else:
                    self.std_words[word_base]=[old_val, word]
            else:
                # import pdb;pdb.set_trace()
                raise Exception("%s in %s, if this is ok - then define with allow_duplicates" % (word_base, self.std_words.keys()))
        else:
            self.std_words[word_base]=word
        return word

    def get_suffixes(self, key):
        key = self.adjust_key(key, self.suffixes_dict.keys())
        if key not in self.suffixes_dict.keys():
            from morphs import BadParamsInitError
            raise BadParamsInitError("Suffix '%s' not one of '%s'" % (key, 
                                     sorted(self.suffixes_dict.keys())))
        return self.suffixes_dict[key] 

    def add_suffixes(self, attrs_key, suff_type, attr_extra="", name4detect="",
                     attrs_ch_ordered=None, suffix_text=None, suffixes_force=None):
        # TODO: control attrs_key - split("/") control values ... etc.
        # TODO: Probably controls in suffix constructor should be moved here - it shouldn't check anything related to word_type
        # TODO: probably there should be some logic for determining which suffix to use when
        from morphs import WordSuffixes
        assert suff_type in self.SUFF_TYPES.keys(), "%s not in %s" % (suff_type, self.SUFF_TYPES.keys())
        # assert attrs_key 
        name = "%s#%s" % (self.code, attrs_key)
        #if attr_extra:
        name += "#"+attr_extra
        name = to_unicode(name)
        assert name not in self.suffixes_dict.keys(), "%s in %s" % (name, self.suffixes_dict.keys())
        if suffix_text:
            assert not suffixes_force, "can't be suffix_text and suffixes_force"
            assert attrs_ch_ordered
            suffixes = WordSuffixes(name=name, attrs_ch_ordered=attrs_ch_ordered, 
                                    suffix_text=suffix_text)
        else:
            assert suffixes_force, "must be suffixes_force when not suffix_text"
            assert not attrs_ch_ordered
            assert isinstance(suffixes_force, WordSuffixes)
            if suffixes_force.name.endswith("__dummy__"):
                suffixes_force.name = name
            suffixes = suffixes_force
        self.suffixes_dict[name] = suffixes
        if suff_type=="MANY":
            assert name4detect
            assert name4detect not in self.suffixes4detection, name4detect
            self.suffixes4detection[name4detect] = suffixes
        else:
            assert not name4detect
        return suffixes

# -----------------------------------------------------

class FixedWordList(object):
    """ only used for unchangeable (fix_words) word types. Contains list of words """
    def __init__(self, word_type_str, attr_to_update_values=None, allow_duplicates=False):
        assert word_type_str in _TYPE_LIST.keys(), "Unknown %s word_type" % word_type_str
        self.allow_duplicates=allow_duplicates
        self.word_type=_TYPE_LIST[word_type_str]
        # TODO: some of these checks should be in word_type class
        assert not self.word_type.attrs_ch, "wt %s shouldn't have ch.attrs - only fix (found %s)" % (self.word_type.code, self.word_type.attrs_ch)
        if self.word_type.attrs_fix:
            assert len(self.word_type.attrs_fix)==1
            assert attr_to_update_values==self.word_type.attrs_fix[0], \
                   "Unknown %s attr for word_type %s" % (attr_to_update_values, word_type)
        else:
            assert not attr_to_update_values
        self.attr_to_update_values=attr_to_update_values
        self.wordset = {}
        self.words = set()
    
    def add_set(self, sub_type, word_list_text):
        assert sub_type not in self.wordset.keys(), sub_type
        if self.attr_to_update_values:
            assert sub_type not in self.attr_to_update_values.values, sub_type
        word_set = [word.lower().strip() for word in word_list_text.split() if word.strip()]
        assert word_set
        _word_set_unicode = set()
        for word_base in word_set:
            # TODO: check if word is valid - not numeric ...
            if not self.allow_duplicates:
                assert word_base not in self.words, "duplicate word '%s'" % w
            if not isinstance(word_base, unicode):
                word_base = unicode(word_base, "utf-8")
            _word_set_unicode.add(word_base)
        word_set = _word_set_unicode
        self.wordset[sub_type]=word_set
        self.words = self.words.union(word_set)
        global _WS_ALL 
        _WS_ALL = _WS_ALL.union(word_set)
        if self.attr_to_update_values:
            self.attr_to_update_values.values.append(sub_type)

    def pp_set(self, sub_type):
        assert sub_type in self.wordset, "%s not in %s" % (sub_type, self.wordset.keys())
        return "\n".join([codecs.encode(w, "utf-8") for w in sorted(self.wordset[sub_type])])


def run_doctests(fname_list):
    assert isinstance(fname_list, (list, tuple)), "invalid input type %s for %r" % (type(fname_list), fname_list)
    for fname in fname_list:
        fname_abs = os.path.join("..", "tests", fname)
        if not os.path.exists(fname_abs):
            print "%s: Not found, skipping" % fname_abs
            continue
        print "%s: running doctests" % fname_abs
        doctest.testfile(fname_abs)


# ==================== CHANGABLE WORDS ====================

def test():
    print "%s: running doctests" % __name__
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    test()

