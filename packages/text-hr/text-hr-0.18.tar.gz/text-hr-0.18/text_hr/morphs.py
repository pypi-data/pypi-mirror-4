# coding=utf-8
# type of words
# doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
"""
More testing of this module is done in form.py
>>> print repr(ALPHABET_STR)
u'abcdefghijklmnoprstuv\u010d\u0107\u0111\u017e\u0161?&~'
>>> ALPHABET_LIST # doctest: +NORMALIZE_WHITESPACE
...    print repr(uni_revert(ch)),
[u'a', u'b', u'c', u'd', u'e', u'f', u'g', u'h', u'i', u'j', u'k', u'l', u'm',
 u'n', u'o', u'p', u'r', u's', u't', u'u', u'v', u'\u010d', u'\u0107',
 u'\u0111', u'\u017e', u'\u0161', u'nj', u'lj', u'd\u017e']

"""
import re
import logging, codecs, datetime
import base
from text_hr.utils import to_unicode
# import vocals

AEIOU = "aeiou"
AEIOUR = AEIOU+"r"
RE_AEIOU_PREPARE = re.compile("[%s]" % (AEIOU, ))
RE_ARA_PREPARE = re.compile("[%s]r[%s]" % (AEIOU, AEIOU))
RE_AEIOUR_SPLITTER = re.compile("[%s]" % AEIOUR)

# TODO: i need this?
logger = logging.getLogger()

# MAP_COMPLEX = (('nj', 'lj'),('%', '&'))
NJ = "?"
LJ = "&"
DZH = "~" # dž
DZ = "^"  # dz

def split_by_last_AEIOU(word):
    if word[-1] in AEIOU:
        base, suff = word[:-1], word[-1]
    else:
        base, suff = word, u""
    return base, suff

def _remove_vc_a(word):
    """
    TODO: solve confusion - remove -> apply and vice versa
    >>> _remove_vc_a("testn")
    u'testan'
    """
    wb, ws = WordSuffixes.apply_vc_A(word, "")
    word = wb + ws
    assert "$" not in word
    assert "%" not in word
    return word

def _apply_vc_a(word):
    """
    TODO: solve confusion - remove -> apply and vice versa
    >>> _apply_vc_a("testan")
    u'testn'
    >>> _apply_vc_a("radio")
    u'radio'
    """
    wb, ws = WordSuffixes.remove_vc_A(word, "")
    word = wb + ws
    assert "$" not in word
    assert "%" not in word
    return word

def count_wparts(word, check_len=True):
    """
    >>> count_wparts("crn")
    1
    >>> count_wparts("ljepši")
    2
    >>> count_wparts(u"ljep")
    1
    >>> count_wparts(u"prednost")
    2
    >>> count_wparts(u"komplikacija")
    5
    >>> count_wparts(u"komplikacij")
    4
    >>> count_wparts(u"piti")
    2
    >>> count_wparts(u"ispiti")
    2

    This is special case:
    >>> count_wparts(u"zarak")
    2
    >>> count_wparts(u"akc")
    1
    """
    word = to_unicode(word)
    w2 = word
    # replace ara -> axa
    w2 = RE_ARA_PREPARE.sub("axa", w2)
    w2 = RE_AEIOUR_SPLITTER.sub("|", w2)
    wparts = 0
    for ws in w2.split("|"):
        if ws:
            wparts+=1 
    if not (w2.startswith("|") or w2.endswith("|")):
        wparts-=1 
    if not (wparts>=1):
        logging.warning("some issue with count_wparts for %s" % word)
        wparts = 1
    # for ch in word[1:]:
    #     if ch in AEIOUR:
    #         wparts+=1
    if check_len:
        assert not(len(word)>=5 and wparts==1), repr(word)
    return wparts

def uni_prepare(s, cp="utf8"):
    """ converts to unicode and replaces nj/lj with % and &, don't forget to call 
    """
    s = to_unicode(s, cp).strip().lower()
    #assert "%" not in s and "&" not in s, s
    return s.replace("nj", NJ).replace("lj", LJ).replace(u"dž",DZH).replace("dz", DZ)

def uni_revert(s):
    """ converts to unicode and replaces nj/lj with % and &, don't forget to call 
    """
    assert isinstance(s, unicode)
    # assert "nj" not in s and "lj" not in s
    return s.replace(NJ, "nj").replace(LJ, "lj").replace(DZH, u"dž").replace(DZ, "dz")

# croatian alphabet
ALPHABET_STR = "".join([chr(cd) for cd in range(ord("a"), ord("z")+1)])
ALPHABET_STR += "čćđžšnjljdž"
for ch in "qxyzw":
    ALPHABET_STR = ALPHABET_STR.replace(ch, "")
ALPHABET_STR = uni_prepare(ALPHABET_STR)
ALPHABET_LIST = [uni_revert(ch) for ch in ALPHABET_STR]

class BadParamsInitError(Exception):
    pass

class WordSuffixes(object):
    @classmethod
    def check_exceptions(cls, keys, exceptions):
        assert isinstance(exceptions, dict)
        for k,v in exceptions.iteritems():
            assert k in keys, "%s not in %s" % (k, keys)
            # TODO: enable same format maybe?
            if isinstance(v, basestring):
                assert len(v.split())==1
                v = [v]
            assert isinstance(v, (tuple, list)), "%s not list %s" % (k,v)


    @classmethod
    def get_suffixes_from_text(cls, keys, suffix_text, exceptions=None):
        suffixes_list = []
        for line in suffix_text.split("\n"):
            line = line.strip()
            if line.startswith("##"):
                continue
            flds = []
            for fld in line.split():
                fld = fld.strip().lower()
                if fld.startswith("##"):
                    break
                if not fld.startswith("#"):
                    flds.append(fld)
            suffixes_list.extend(flds)
        suffixes = dict([(k, s.split("|")) for k, s in zip(keys, suffixes_list)])
        assert len(keys)==len(suffixes_list), "%d!=%d" % (len(keys), len(suffixes_list))
        if exceptions:
            assert isinstance(exceptions, dict)
            #self.check_exceptions(keys, exceptions)
            for k,v in exceptions.iteritems():
                # if index fails then 
                try:
                    suffixes_list[keys.index(k)]=v
                except ValueError, e:
                    raise Exception("%s not in %s" % (k, keys))
                suffixes[k]=v
                #suffixes_list = ["OBSOLETE - APPLIED exceptions %s\norig_list: %s" % (self.exceptions, self.suffixes_list)]
            # TODO: this can be done too - get first line split an format well: 
            # self.suffix_text =  ... self.suffix_list
            self.suffix_text = "OBSOLETE - APPLIED exceptions %s\norig_text: %s" % (exceptions, suffix_text)
        return suffixes_list, suffixes

    def __init__(self, name, attrs_ch_ordered, suffix_text, 
                 suffixes_force=None, exceptions=None, based_on=None):
        """ last 3 attrs are used only in copy mode 
            ## line ignored
            #  word ignored
            0  no suffix
            -  case inpossible
            letter(s) - normal suffix
            sufix1|sufix2 - first or another possible
            -Num - strip Num chars from lexem, e.g. -1em on "test" will produce "tesem"
            !wordform - forces wordform
            %Xletter(s) - means apply change X on letters after
                - e.g. nepostojano A, %Aa on ovakav (suffix) -> ovakava (vc-A) -> ovakav 
        """
        name_flds = name.split("#")
        # assert len(name_flds)>1, name_flds
        word_type_str = name_flds[0]
        assert base.is_word_type_registred(word_type_str), "Unknown %s word_type" % word_type_str
        self._name = None
        self.name = name

        self.based_on = []
        if based_on:
            self.based_on.append(based_on)
        for attr in attrs_ch_ordered:
            assert isinstance(attr, base.WordAttr), attr
            assert attr.can_ch, attr
        self.attrs_ch_ordered = attrs_ch_ordered

        self.keys = []
        i = self.fill_keys(self.keys, "", self.attrs_ch_ordered[:])
        len_exp = 1
        for attr in self.attrs_ch_ordered:
            lv = len(attr.values)
            assert lv, attr
            len_exp *= lv
        self.exceptions = exceptions
        if suffix_text:
            assert not suffixes_force
            self.suffix_text = suffix_text
            self.suffixes_list, self.suffixes = self.get_suffixes_from_text(
                                                    self.keys, 
                                                    self.suffix_text, 
                                                    self.exceptions)
            self.length=len(self.suffixes_list)
        else:
            assert suffixes_force
            assert isinstance(suffixes_force, dict)
            self.suffixes_list = ["forced suffixes"]
            self.suffix_text = "forced suffixes"
            self.suffixes = suffixes_force.copy()
            self.length=len(self.suffixes)
            if self.exceptions:
                # TODO: maybe this deserves function ...
                self.check_exceptions(self.keys, self.exceptions)
                #self.check_exceptions(self.exceptions)
                for k,v in self.exceptions.iteritems():
                    self.suffixes[k]=v
                self.suffixes_list = ["OBSOLETE - APPLIED exceptions %s\norig_list: %s" % (self.exceptions, self.suffixes_list)]
                self.suffix_text = "OBSOLETE - APPLIED exceptions %s\norig_text: %s" % (self.exceptions, self.suffix_text)
        assert len_exp==self.length, "suffixes number doesn't match expected %d, found %d in %s" % (len_exp, self.length, self.suffixes_list)
        assert len(self.keys)==self.length, "%d!=%d" % (len(self.keys), self.length)

    def _set_name(self, name):
        if self._name:
            assert self._name==name or self._name.endswith("__dummy__"), "%s<-%s" % (self._name, name)
        self._name = name

    def _get_name(self):
        return self._name
    name = property(_get_name, _set_name)          

    def copy(self, name, exceptions=None):
        """ returns new WordSuffixes object as copy of this one with applied exceptions"""
        #return self.apply_exceptions(name=name, exceptions=exceptions)
        #name = self.name + "__COPY__"
        # NOTE: already checked in constructor
        # self.check_exceptions(self.keys(), exceptions)
        # self.check_exceptions(exceptions)
        new_object = WordSuffixes(name=name, attrs_ch_ordered=self.attrs_ch_ordered, 
                                  suffix_text="", suffixes_force=self.suffixes, 
                                  exceptions=exceptions, based_on=self)
        return new_object
         
    def union(self, name, suffixes_obj_other):
        assert self.name!=suffixes_obj_other.name
        new_object = self.copy(name=name)
        new_object.suffixes = self.union_suffixes(self.suffixes, suffixes_obj_other.suffixes)
        new_object.based_on.append(suffixes_obj_other) 
        return new_object

    @classmethod
    def union_suffixes(cls, suffixes, suffixes_other):
        """
        >>> suffixes = {
        ... "aa" : ["1","2"],
        ... "ac" : ["-"],
        ... "ad" : ["-"],
        ... "ab" : ["1","2"]}

        >>> suffixes_other = {
        ... "aa" : ["1"],
        ... "ac" : ["-"],
        ... "ad" : ["4"],
        ... "ab" : ["2", "3"]}

        >>> print WordSuffixes.union_suffixes(suffixes, suffixes_other)
        {'aa': ['1', '2'], 'ac': ['-'], 'ab': ['1', '2', '3'], 'ad': ['4']}
        """
        assert len(suffixes)==len(suffixes_other)
        result = {}
        for k, s_list in suffixes.iteritems():
            assert k in suffixes_other
            assert k not in result

            result[k] = [s for s in s_list if s!="-"]

            assert len(s_list)>0
            if s_list[0]=="-":
                assert len(s_list)==1

            s_list_other = suffixes_other[k]
            assert len(s_list_other)>0
            if s_list_other[0]=="-":
                assert len(s_list_other)==1

            for s_other in s_list_other:
                if s_other!="-" and s_other not in s_list:
                    result[k].append(s_other)
            if len(result[k])==0:
                result[k] = ["-"]
        return result 

    @classmethod
    def get_vc_dict(cls):
        """
        list:
            nepostojano A
                apply_vc_A
            gubljenje suglasnika - duplicates and l|n + j goes to base as lj/nj
                apply_vc_D
            jotacija
                apply_vc_J
            vokalizacija
                apply_vc_L
            jednačenje po mjestu tvorbe 
                apply_vc_M
            jednačenje po zvučnosti 
                apply_vc_Z
            palatalizacija 
                apply_vc_P
            sibilarizacija 
                apply_vc_S
            nisam 
        - nepostojano e
        - izmjenjivanje i|e|je|ije

        Get vocal changes dict:

        >>> d = WordSuffixes.get_vc_dict()
        >>> print "\\n".join(["%s=has_apply=%s, has_remove=%s" % (k,d[k][0] is not None, d[k][1] is not None) 
        ... for k in sorted(d.keys())])
        A=has_apply=True, has_remove=True
        D=has_apply=True, has_remove=True
        J=has_apply=True, has_remove=True
        L=has_apply=True, has_remove=True
        M=has_apply=True, has_remove=True
        P=has_apply=True, has_remove=True
        S=has_apply=True, has_remove=True
        Z=has_apply=True, has_remove=True
        """
        if not getattr(cls, "vc_dict", None):
            cls.vc_dict = {}
            apply_text = "apply_vc_"
            remove_text = "remove_vc_"
            for prop in dir(cls):
                if prop.startswith(apply_text):
                    key = prop[len(apply_text):]
                    if key not in cls.vc_dict:
                        cls.vc_dict[key]=[getattr(cls, prop), None]
                    else:
                        cls.vc_dict[key][0]=getattr(cls, prop)
                if prop.startswith(remove_text):
                    key = prop[len(remove_text):]
                    if key not in cls.vc_dict:
                        cls.vc_dict[key]=[None, getattr(cls, prop)]
                    else:
                        cls.vc_dict[key][1]=getattr(cls, prop)
        return cls.vc_dict

    DONT_APPLY_VC_A_SUFF2 = ("st", u"št", u"šć", "zd", u"žd")

    @classmethod
    def apply_vc_A(cls, base, suffix, trace_vc_list=None):
        """
        Nepostojano A: 
        This one with remove_vc_Z - bezv->zvuc
        >>> WordSuffixes.apply_vc_A("pripovjetk", "a")
        (u'pripovjedak', u'a')

        >>> WordSuffixes.apply_vc_A("brak", "a")
        (u'brak', u'a')

        >>> WordSuffixes.apply_vc_A("brak", "")
        (u'brak', u'')

        >>> WordSuffixes.apply_vc_A("brz", "a")
        (u'brz', u'a')

        >>> WordSuffixes.apply_vc_A("borc", "")
        (u'borac', u'')
        >>> WordSuffixes.apply_vc_A("borc", "a")
        (u'borac', u'a')
        >>> WordSuffixes.apply_vc_A("ovakv", "")
        (u'ovakav', u'')
        >>> WordSuffixes.get_vocal_change("A")("nikakv", "")
        (u'nikakav', u'')
        >>> WordSuffixes.get_vocal_change("A")("navij", "ati")
        (u'navij', u'ati')
        >>> WordSuffixes.get_vocal_change("A")("nav", "iti")
        (u'nav', u'iti')
        >>> WordSuffixes.get_vocal_change("A")("sv", "")
        (u'sav', u'')
        >>> vc_list = []
        >>> WordSuffixes.apply_vc_A("ovakv", "", vc_list)
        (u'ovakav', u'')
        >>> vc_list 
        ['+A']
        """
        base = uni_prepare(base)
        suffix = uni_prepare(suffix)

        if base and base[-2:] not in cls.DONT_APPLY_VC_A_SUFF2:
            #f = base + suffix
            p_last = len(base)-1 
            # exception - when r acts like AEIOU - don't apply vc
            #   -3 -2 -1
            #   b  r  z - don't apply
            # b o  r  c - apply
            if (p_last>=1 and base[-2] not in AEIOU and base[-1] not in AEIOU):
                if p_last<2 or not (p_last>=2 and base[-3] not in AEIOU and base[-2]=="r"):
                    # orig: base = bb[:-1]+"a"+base[-1]
                    # bb,bs = base[:-1], base[-1:]
                    # TODO: is there a way to generalize similar calls?
                    bb,bs = cls._apply_vc_PS("-Z2", "remove", base[:-1], base[-1:], 
                                             cls.MAPPING_Z, cls.MAPPING_Z_BEZV, trace_vc_list)
                    # bb,bs = cls.remove_vc_Z(base[:-1],base[-1:], trace_vc_list)
                    base = bb + "a" + bs

                    if trace_vc_list is not None:
                        trace_vc_list.append("+A")
        return uni_revert(base), uni_revert(suffix)

    @classmethod
    def remove_vc_A(cls, base, suffix, trace_vc_list=None):
        """
        Nepostojano A: 

        You can't know when to apply and when not when having R:
              -1 0 +1
            t  r a  g  - don't apply
            to r a  nj - apply
        if single or 2nd then don't apply:
        >>> WordSuffixes.remove_vc_A("brak", "")
        (u'brak', u'')
        >>> WordSuffixes.remove_vc_A("brak", "a")
        (u'brak', u'a')
        >>> WordSuffixes.remove_vc_A("trag", "a")
        (u'trag', u'a')

        not single
        >>> WordSuffixes.remove_vc_A("brekav", "")
        (u'brekv', u'')

        >>> WordSuffixes.remove_vc_A("radio", "")
        (u'radio', u'')
        >>> WordSuffixes.remove_vc_A("ovakav", "a")
        (u'ovakv', u'a')
        >>> WordSuffixes.remove_vc_A("nikakav", "a")
        (u'nikakv', u'a')
        >>> WordSuffixes.remove_vc_A("navij", "ati")
        (u'navij', u'ati')
        >>> WordSuffixes.remove_vc_A("nav", "iti")
        (u'nav', u'iti')
        >>> WordSuffixes.remove_vc_A("nekakav", "")
        (u'nekakv', u'')
        >>> WordSuffixes.remove_vc_A("vrabac", "a")
        (u'vrapc', u'a')

        >>> WordSuffixes.remove_vc_A(*WordSuffixes.apply_vc_L("kabao", "a"))
        (u'kabl', u'a')

        >>> WordSuffixes.remove_vc_A("misao", "")
        (u'misl', u'')

        >>> WordSuffixes.remove_vc_A("ugao", "a")
        (u'ugl', u'a')

        >>> WordSuffixes.remove_vc_A("misao", "")
        (u'misl', u'')

        >>> WordSuffixes.remove_vc_A("toranj", "evi")
        (u'tornj', u'evi')

        single - don't apply
        >>> WordSuffixes.remove_vc_A("kralj", "evi")
        (u'kralj', u'evi')

        Test jotacija:
        >>> WordSuffixes.remove_vc_A("ćzataj", "e")
        (u'\u0107za\u0107', u'e')

        Test remove duplicates:
        >>> WordSuffixes.remove_vc_A("zatat", "e")
        (u'zat', u'e')
        >>> WordSuffixes.remove_vc_A("zarar", "e")
        (u'zar', u'e')

        >>> WordSuffixes.get_vocal_change("-A")("zarar", "e")
        (u'zar', u'e')

        >>> vc_list = []
        >>> WordSuffixes.remove_vc_A("toranj", "evi", vc_list)
        (u'tornj', u'evi')
        >>> vc_list
        ['-A']
        >>> WordSuffixes.remove_vc_A("tornj", "evi", vc_list)
        (u'tornj', u'evi')
        >>> vc_list
        ['-A']
        """
        assert base
        assert "%" not in base and "&" not in base, "base=%s -> replace nj/lj with %% and & - failed, chars found" % base
        p1 = base.rfind("a")
        if not p1>1: # not 2nd char
            base = uni_prepare(base)
            suffix = uni_prepare(suffix)
            return uni_revert(base), uni_revert(suffix)

        if suffix=="":
            bb, bs = cls.apply_vc_L(base, "a", trace_vc_list)
            base = bb
        base, suffix = cls.apply_vc_L(base, suffix, trace_vc_list)
        base = uni_prepare(base)
        suffix = uni_prepare(suffix)

        all_aeiou = RE_AEIOU_PREPARE.findall(base)
        p1 = base.rfind("a")
        if len(all_aeiou)>1 and p1>1: # not only and not 2nd char
            p_last = len(base)-1 
            # TODO: check if not too close to begging
            if p1 in (p_last-1,): # "only next to last char must be a '%s'" % base
                if base[p1-1] not in AEIOU and base[p1+1] not in AEIOU:
                    if trace_vc_list is not None:
                        trace_vc_list.append("-A")
                    # drop a
                    bb,bs = base[:p1], base[p1+1:]
                    # NOTE: M is called inside Z and then J again
                    bb,bs = cls.apply_vc_Z(bb, bs, trace_vc_list)
                    bb,bs = cls.apply_vc_J(bb, bs, trace_vc_list)
                    bb,bs = cls.apply_vc_D(bb, bs, trace_vc_list)
                    base = bb + bs
        return uni_revert(base), uni_revert(suffix)

    # jednačenje po mjestu tvorbe - str 67
    # szh i n
    #
    # gubljenje duplih samoglasnika preddvorje -> predvorje

    # navezak - og -> oga, om -> omu, ome, im->ima, ime
    # tad->tada, sad, sada, kad, kada, nikad, nikada, 
    # s, sa, k, ka, nad, nada, pod poda, pred preda, uz, uza, iz iza, t250

    # vokalizacija
    # na kraju sloga l -> o, čitao->čitala, učio->učila...

   # TODO: not done jotacija
   #  MAPPINGS.add_mapping("", "Jotacija-bpmv",  ["bj",   "pj",   "mj",   "vj"], 
   #                                              ["blj", "plj", "mlj", "vlj"],
   #                                              "j")
    @classmethod
    def remove_vc_D(cls, base, suffix, trace_vc_list=None):
        raise NotImplementedError("not now")
    
    @classmethod
    def apply_vc_D(cls, base, suffix, trace_vc_list=None):
        """Gubljenje suglasnika - duplicates and l|n + j goes to base as lj/nj
        >>> WordSuffixes.apply_vc_D(u'pi', u'jemo')
        (u'pi', u'jemo')
        >>> WordSuffixes.apply_vc_D("pred", "duplo")
        (u'pred', u'uplo')
        >>> WordSuffixes.apply_vc_D("šmisl", "ju")
        (u'\u0161mi\u0161lj', u'u')
        >>> WordSuffixes.apply_vc_D("toran", "j")
        (u'toranj', u'')
        >>> WordSuffixes.apply_vc_D("vidje", "o")
        (u'vidi', u'o')
        >>> WordSuffixes.apply_vc_D("šdonosi", "jen")
        (u'\u0161dono\u0161', u'en')
        >>> vc_list = []
        >>> WordSuffixes.apply_vc_D("pred", "duplo", vc_list)
        (u'pred', u'uplo')
        >>> vc_list
        ['+D0']
        >>> vc_list = []
        
        Later this will report problem ;)
        >>> WordSuffixes.apply_vc_D("šdonosi", "jen", vc_list)
        (u'\u0161dono\u0161', u'en')
        >>> vc_list
        ['+D4', '+J0', '+D5']
        """
        base = uni_prepare(base)
        suffix = uni_prepare(suffix)
        if base and suffix:
            # TODO: this is not good solved!
            #    here is part for: poni ima -> poni j ima
            #    but not for:      radi + imo -> radimo (this is is get_form)
            if suffix and suffix[0] not in AEIOU and base[-1]==suffix[0]:
            # if suffix and base[-1]==suffix[0]:
                suffix = suffix[1:]
                if trace_vc_list is not None:
                    trace_vc_list.append("+D0")

            if suffix:
                if base[-1]=="l" and suffix[0]=="j":
                    base = base[:-1]+LJ
                    suffix = suffix[1:]
                    if trace_vc_list is not None:
                        trace_vc_list.append("+D1")
                elif base[-1]=="n" and suffix[0]=="j":
                    base = base[:-1]+NJ
                    suffix = suffix[1:]
                    if trace_vc_list is not None:
                        trace_vc_list.append("+D2")
                # vidje+o -> vidi+o
                elif base.endswith("je") and suffix=="o":
                    base = base[:-2]+"i"
                    if trace_vc_list is not None:
                        trace_vc_list.append("+D3")
                # donosi + jen -> donosj + en -> donoš + en
                elif (    len(base)>=2 and base[-2] in cls.VC_J_CHARLIST_FROM 
                      and base.endswith("i") and suffix.startswith("je")):
                    bb1, bs1 = base[:-1], "j"
                    if trace_vc_list is not None:
                        trace_vc_list.append("+D4")
                    bb2, bs2 = cls.apply_vc_J(bb1, bs1, trace_vc_list)
                    if bb1!=bb2:
                        base = bb2 + bs2
                        suffix = suffix[1:]
                        if trace_vc_list is not None:
                            trace_vc_list.append("+D5")
                if len(base)>1:
                    bb, bs = cls.apply_vc_M(base[:-1], base[-1], trace_vc_list)
                    base = bb + bs
        return uni_revert(base), uni_revert(suffix)

    # ------------------- jotacija ---------------------------
    VC_J_CHARLIST_FROM=u"cdghkstz"
    # NOTE: question to unicode? usually i need this: unicode("čđžščšćž", "utf-8")
    #       but here this works too (usually it doesn't) - and it is really correct
    VC_J_CHARLIST_TO  = u"čđžščšćž"
    assert len(VC_J_CHARLIST_FROM)==len(VC_J_CHARLIST_TO)
    MAPPING_J=([ch for ch in VC_J_CHARLIST_FROM], # NOTE: "lj", "nj" not done, that is done in D
               [ch for ch in VC_J_CHARLIST_TO  ])
    LIST_J_L=[u"b", u"p", u"m", u"v"]
    @classmethod
    def remove_vc_J(cls, base, suffix, trace_vc_list=None):
        raise NotImplementedError("not now")
    
    @classmethod
    def apply_vc_J(cls, base, suffix, trace_vc_list=None):
        """jotacija
        NOTE: n+j->NJ and l+j->LJ not done here ... but later/before when replacing nj and lj with some spec char
        >>> WordSuffixes.apply_vc_J("ćtret", "ji")
        (u'\u0107tre\u0107', u'i')
        >>> WordSuffixes.apply_vc_J("žbrz", "ji")
        (u'\u017ebr\u017e', u'i')
        >>> WordSuffixes.apply_vc_J("đglod", "jem")
        (u'\u0111glo\u0111', u'em')
        >>> WordSuffixes.apply_vc_J("tan", "ji")
        (u'tan', u'ji')
        >>> WordSuffixes.apply_vc_J("špis", "jem")
        (u'\u0161pi\u0161', u'em')

        >>> WordSuffixes.apply_vc_J("špišs", "jem")
        (u'\u0161pi\u0161', u'em')

        >>> vc_list = []
        >>> WordSuffixes.apply_vc_J("šćradost", "ju", vc_list)
        (u'\u0161\u0107rado\u0161\u0107', u'u')
        >>> vc_list
        ['+J0', '+M']

        TODO: it seems that I messed things up - mis+lju is vc M and is already done :(
        # TODO: this I didn't found in book: s+lj -> šlj. Needs checking
        #     NOTE: currently implemented: mis+lju -> mišlju
        # TODO: check if is this true: mis+ju -> misl+ju -> mis+lju -> mišlju
        # >>> vc_list = []
        # >>> WordSuffixes.apply_vc_J("šmis", "lju", vc_list)
        # (u'\u0161mi\u0161', u'lju')
        # >>> vc_list
        # ['+J2']
        # >>> WordSuffixes.apply_vc_J("šnos", "nja")
        # (u'\u0161no\u0161', u'nja')
        # >>> WordSuffixes.apply_vc_J("šćradost", "lju")
        # (u'\u0161\u0107radost', u'lju')

        Epentetsko L
        >>> vc_list = []
        >>> WordSuffixes.apply_vc_J("grub", "ji", vc_list)
        (u'grublj', u'i')
        >>> vc_list
        ['+J1']
        >>> WordSuffixes.apply_vc_J("grm", "je")
        (u'grmlj', u'e')
        >>> vc_list = []
        >>> WordSuffixes.apply_vc_J("smi", "jem", vc_list)
        (u'smi', u'jem')
        >>> vc_list
        []
        """
        base = uni_prepare(base)
        suffix = uni_prepare(suffix)
        if base and suffix:
            if suffix and suffix[0] in ("j", NJ, LJ):
                match = False
                if suffix[0]=="j":
                    if base[-1] in cls.MAPPING_J[0]:
                        bb, bs = base[:-1], cls.MAPPING_J[1][cls.MAPPING_J[0].index(base[-1])]
                        match = True
                        if trace_vc_list is not None:
                            trace_vc_list.append("+J0")
                    elif base[-1] in cls.LIST_J_L:
                        bb, bs = base, LJ
                        match=True
                        if trace_vc_list is not None:
                            trace_vc_list.append("+J1")
                # elif base[-1] in ("s"):
                #     bb, bs = base[:-1], cls.MAPPING_J[1][cls.MAPPING_J[0].index(base[-1])]
                #     match = True
                #     if trace_vc_list is not None:
                #         trace_vc_list.append("+J2")
                if match:
                    bb, bs = cls.apply_vc_D(bb, bs, trace_vc_list)
                    bb, bs = cls.apply_vc_M(bb, bs, trace_vc_list)
                    base=bb + bs
                    if suffix[0]=="j":
                        suffix = suffix[1:]
        return uni_revert(base), uni_revert(suffix)

    # ------------------- vokalizacija ---------------------------
    @classmethod
    def remove_vc_L(cls, base, suffix, trace_vc_list=None):
        raise NotImplementedError("not now")
    
    @classmethod
    def apply_vc_L(cls, base, suffix, trace_vc_list=None):
        """vokalizacija
        >>> WordSuffixes.apply_vc_L("andjeo", "a")
        (u'andjel', u'a')
        >>> vc_list = []
        >>> base, suffix = WordSuffixes.apply_vc_L("kabao", "a", vc_list)
        >>> base, suffix 
        (u'kabal', u'a')
        >>> WordSuffixes.remove_vc_A(base, suffix, vc_list)
        (u'kabl', u'a')
        >>> vc_list
        ['+L0', '-A']
        """
        base = uni_prepare(base)
        suffix = uni_prepare(suffix)
        if base and suffix:
            p_last = len(base)-1 
            if suffix and p_last>=1 and base[-2] in "aeiu" and base[-1] in "o" and suffix[0] in AEIOU:
                base=base[:-1]+"l"
                if trace_vc_list is not None:
                    trace_vc_list.append("+L0")
        return uni_revert(base), uni_revert(suffix)

    # ------------------- jednačenje po mjestu tvorbe ---------------------------
    @classmethod
    def remove_vc_M(cls, base, suffix, trace_vc_list=None):
        return cls._apply_vc_M("remove", base, suffix, trace_vc_list)
    
    @classmethod
    def apply_vc_M(cls, base, suffix, trace_vc_list=None):
        return cls._apply_vc_M("apply", base, suffix, trace_vc_list)

    @classmethod
    def _apply_vc_M(cls, mode, base, suffix, trace_vc_list=None):
        """jednačenje po mjestu tvorbe
        >>> WordSuffixes.apply_vc_M("šćrados", "ću")
        (u'\u0161\u0107rado\u0161', u'\u0107u')
        >>> WordSuffixes.apply_vc_M("šbijes", "nji")
        (u'\u0161bije\u0161', u'nji')
        >>> WordSuffixes.apply_vc_M("šmis", "lju")
        (u'\u0161mi\u0161', u'lju')
        >>> WordSuffixes.apply_vc_M("žpaz", "nja")
        (u'\u017epa\u017e', u'nja')
        >>> WordSuffixes.apply_vc_M("obran", "ben")
        (u'obram', u'ben')
        >>> vc_list = []
        >>> WordSuffixes.apply_vc_M("crn", "purast", vc_list)
        (u'crm', u'purast')
        >>> vc_list
        ['+M']
        >>> WordSuffixes.apply_vc_M("šmjeh", "čić")
        (u'\u0161mje\u0161', u'\u010di\u0107')
        >>> WordSuffixes.apply_vc_M("šorah", "čić")
        (u'\u0161ora\u0161', u'\u010di\u0107')

        >>> WordSuffixes.remove_vc_M("radoš", "ću")
        ([u'rados', u'radoh'], u'\u0107u')
        >>> WordSuffixes.remove_vc_M("biješ", "nji")
        (u'bijes', u'nji')
        >>> WordSuffixes.remove_vc_M("oraš", "čić")
        ([u'oras', u'orah'], u'\u010di\u0107')

        >>> WordSuffixes.remove_vc_M("miš", "lju")
        (u'mis', u'lju')

        >>> WordSuffixes.remove_vc_M("paž", "nja")
        (u'paz', u'nja')

        >>> WordSuffixes.remove_vc_M("obram", "ben")
        (u'obran', u'ben')
        >>> vc_list = []
        >>> WordSuffixes.remove_vc_M("crm", "purast", vc_list)
        (u'crn', u'purast')
        >>> vc_list
        ['-M']
        """
        assert mode in ("remove", "apply")
            
        base = uni_prepare(base)
        suffix = uni_prepare(suffix)
        if base and suffix:
            # TODO: maybe needs some optimization
            match = False
            if mode=="apply":
                if   base[-1]=="s" and suffix[0] in u"čć"+NJ+LJ:
                    base=base[:-1]+u'š'
                    match = True
                elif base[-1]=="z" and suffix[0] in u"đ"+DZH+NJ+LJ:
                    base=base[:-1]+u'ž'
                    match = True
                elif base[-1]=="n" and suffix[0] in "bp":
                    base=base[:-1]+u'm'
                    match = True
                elif base[-1]=="h" and suffix[0] in u"čć":
                    base=base[:-1]+u'š'
                    match = True
                if match and trace_vc_list is not None:
                    trace_vc_list.append("+M")
            else:
                if   base[-1]==u"š" and suffix[0] in u"čć"+NJ+LJ:
                    if base[-1]==u"š" and suffix[0] in u"čć":
                        # returns more candidates
                        if trace_vc_list is not None:
                            trace_vc_list.append("-M?")
                        return [uni_revert(base[:-1]+'s'), uni_revert(base[:-1]+u'h')], uni_revert(suffix) 
                    base=base[:-1]+'s'
                    match = True
                elif base[-1]==u"ž" and suffix[0] in u"đ"+DZH+NJ+LJ:
                    base=base[:-1]+'z'
                    match = True
                elif base[-1]=="m" and suffix[0] in "bp":
                    base=base[:-1]+u'n'
                    match = True
                if match and trace_vc_list is not None:
                    trace_vc_list.append("-M")
        return uni_revert(base), uni_revert(suffix)

    # ------------------- jednačenje po zvučnosti ---------------------------
    MAPPING_Z=([u"b", u"d", u"g", u'z', u'ž', u'' , u'' , DZ, DZH, u'đ'],  #zvučnik
               [u"p", u"t", u"k", u's', u'š', u'f', u'h', u'c' , u'č' , u'ć'])  #bezvučn

    MAPPING_Z_ZVUC = "".join(MAPPING_Z[0])
    MAPPING_Z_BEZV = "".join(MAPPING_Z[1])

    @classmethod
    def remove_vc_Z(cls, base, suffix, trace_vc_list=None):
        """jednačenje po zvučnosti - revert
        >>> WordSuffixes.remove_vc_Z("vrap", "c")
        (u'vrab', u'c')
        >>> WordSuffixes.remove_vc_Z("glat", "k")
        (u'glad', u'k')
        >>> WordSuffixes.remove_vc_Z("đrić", "ka")
        (u'\u0111ri\u0111', u'ka')
        >>> WordSuffixes.remove_vc_Z("žeš", "ka")
        (u'\u017ee\u017e', u'ka')

        >>> WordSuffixes.remove_vc_Z("tob", "dž")
        (u'top', u'd\u017e')
        >>> WordSuffixes.remove_vc_Z("svag", "danji")
        (u'svak', u'danji')

        >>> vc_list = []
        >>> WordSuffixes.remove_vc_Z("is", "čistiti", vc_list)
        (u'iz', u'\u010distiti')
        >>> vc_list
        ['-Z2']
        >>> vc_list = []
        >>> WordSuffixes.remove_vc_Z("iš", "čistiti", vc_list)
        (u'iz', u'\u010distiti')
        >>> vc_list
        ['-M?', '-Z2']

        >>> WordSuffixes.remove_vc_Z("kras", "ti")
        (u'kras', u'ti')

        >>> WordSuffixes.get_vocal_change("-Z")("iš", "čistiti")
        (u'iz', u'\u010distiti')
        """
        # zvuc = "".join(cls.MAPPING_Z[0])
        # bezv = "".join(cls.MAPPING_Z[1])
        base_or_bases, suffix = cls.remove_vc_M(base, suffix, trace_vc_list)
        if isinstance(base_or_bases, (list, tuple)):
            # NOTE: if more results - then take first one
            base = base_or_bases[0]
        else:
            base = base_or_bases
        # TODO: maybe needed base = uni_prepare(base)
        #       suffix = uni_prepare(suffix)
        # 2. zv + zv -> bezv[zv] + zv
        if base and suffix: 
            # TODO: check before was ("st",):
            if base[-1]+suffix[0] not in cls.DONT_APPLY_VC_A_SUFF2: 
                base, suffix = cls._apply_vc_PS("-Z1", "apply" , base, suffix, cls.MAPPING_Z, cls.MAPPING_Z_ZVUC, trace_vc_list)
                # 1. bezv + bezv -> zv[bezv] + bezv
                base, suffix = cls._apply_vc_PS("-Z2", "remove", base, suffix, cls.MAPPING_Z, cls.MAPPING_Z_BEZV, trace_vc_list)
        return uni_revert(base), uni_revert(suffix)
    
    @classmethod
    def apply_vc_Z(cls, base, suffix, trace_vc_list=None):
        """jednačenje po zvučnosti
        >>> WordSuffixes.remove_vc_Z("pripovjet", "ka")
        (u'pripovjed', u'ka')
        >>> WordSuffixes.apply_vc_Z("vrab", "c")
        (u'vrap', u'c')
        >>> WordSuffixes.apply_vc_Z("glad", "k")
        (u'glat', u'k')
        >>> WordSuffixes.apply_vc_Z("ćriđ", "ka")
        (u'\u0107ri\u0107', u'ka')
        >>> WordSuffixes.apply_vc_Z("žež", "ka")
        (u'\u017ee\u0161', u'ka')

        >>> WordSuffixes.apply_vc_Z("top", "dž")
        (u'tob', u'd\u017e')
        >>> WordSuffixes.apply_vc_Z("svak", "danji")
        (u'svag', u'danji')

        >>> vc_list = []
        >>> "".join(WordSuffixes.apply_vc_Z("s", "Bogom", vc_list))
        u'zbogom'
        >>> vc_list
        ['+Z2']
        >>> WordSuffixes.apply_vc_Z("šiz", "čistiti")
        (u'\u0161i\u0161', u'\u010distiti')
        """
        # zvuc = "".join(cls.MAPPING_Z[0])
        # bezv = "".join(cls.MAPPING_Z[1])
        # 1. zv + bezv -> bezv[zv] + bezv
        base, suffix = cls._apply_vc_PS("+Z1", "apply" , base, suffix, cls.MAPPING_Z, cls.MAPPING_Z_BEZV, trace_vc_list)
        # 2. bezv + zv -> zv[bezv] + zv
        base, suffix = cls._apply_vc_PS("+Z2", "remove", base, suffix, cls.MAPPING_Z, cls.MAPPING_Z_ZVUC, trace_vc_list)
        base, suffix = cls.apply_vc_M(base, suffix, trace_vc_list)
        return base, suffix


    # ------------------- palatalizacija ---------------------------
    MAPPING_P=([u"k", u"g", u"h"], [u"č", u"ž", u"š"])

    @classmethod
    def apply_vc_P(cls, base, suffix, trace_vc_list=None):
        return cls._apply_vc_PS("+P", "apply", base, suffix, cls.MAPPING_P, "iea", trace_vc_list)
    @classmethod
    def remove_vc_P(cls, base, suffix, trace_vc_list=None):
        return cls._apply_vc_PS("-P", "remove", base, suffix, cls.MAPPING_P, "iea", trace_vc_list)
        
    # ------------------- sibilarizacija ---------------------------
    MAPPING_S=([u"k", u"g", u"h"], [u"c", u"z", u"s"])

    @classmethod
    def apply_vc_S(cls, base, suffix, trace_vc_list=None):
        return cls._apply_vc_PS("+S", "apply", base, suffix, cls.MAPPING_S, "i", trace_vc_list)
    @classmethod
    def remove_vc_S(cls, base, suffix, trace_vc_list=None):
        return cls._apply_vc_PS("-S", "remove", base, suffix, cls.MAPPING_S, "i", trace_vc_list)

    # ------------------- common method P/S/Z ---------------------------
    @classmethod
    def _apply_vc_PS(cls, vc_code, mode, base, suffix, mapping, vocals, trace_vc_list=None):
        """
        Sibilarizacija
        >>> WordSuffixes.apply_vc_S("majk", "i")
        (u'majc', u'i')
        >>> WordSuffixes.apply_vc_S("majk", "e")
        (u'majk', u'e')
        >>> vc_list = []
        >>> WordSuffixes.apply_vc_S("jarug", "i", vc_list)
        (u'jaruz', u'i')
        >>> vc_list
        ['+S']
        >>> vc_list = []
        >>> WordSuffixes.apply_vc_S("jarug", "u", vc_list)
        (u'jarug', u'u')
        >>> vc_list
        []

        >>> WordSuffixes.remove_vc_S("krčaz", "i")
        (u'kr\u010dag', u'i')
        >>> vc_list = []
        >>> WordSuffixes.remove_vc_S("pec", "i", vc_list)
        (u'pek', u'i')
        >>> vc_list
        ['-S']

        Palatalizacija
        >>> vc_list = []
        >>> WordSuffixes.apply_vc_P("junak", "e", vc_list)
        (u'juna\u010d', u'e')
        >>> vc_list
        ['+P']
        >>> WordSuffixes.apply_vc_P("junak", "u")
        (u'junak', u'u')
        >>> vc_list = []
        >>> WordSuffixes.remove_vc_P("junač", "e", vc_list)
        (u'junak', u'e')
        >>> vc_list
        ['-P']
        >>> WordSuffixes.remove_vc_P("junak", "u")
        (u'junak', u'u')

        TODO: this can be optimized - dict, vocals, etc 
        """
        base = uni_prepare(base)
        suffix = uni_prepare(suffix)
        if base and suffix:
            assert mode in ("remove", "apply")
            if mode=="apply":
                map_from, map_to = 0, 1
            else:
                map_from, map_to = 1, 0
            # if applied_vcs and "A" in applied_vcs:
            #     vocals+="a"
            if base[-1] in mapping[map_from] and suffix and suffix[0] in vocals:
                to = mapping[map_to][mapping[map_from].index(base[-1])]
                base=base[:-1]+to
                if trace_vc_list is not None:
                    trace_vc_list.append(vc_code)
        return uni_revert(base), uni_revert(suffix)

    @classmethod
    def get_vocal_change(cls, vc):
        name = "apply"
        if vc.startswith("-"):
            name = "remove"
            vc = vc[1:]
        assert hasattr(cls, "%s_vc_%s" % (name, vc.upper())), vc
        return getattr(cls, "%s_vc_%s" % (name, vc.upper()))

    @classmethod
    def fill_keys(cls, keys, key, attrs_left, i=0):
        assert attrs_left
        attr = attrs_left[0]
        is_last_dim = len(attrs_left)==1
        for v in attr.values:
            #key_new = "%s%s=%s" % ((key and "+" or ""), attr.code,v)
            key_new = "%s%s%s" % (key, (key and "/" or ""), v)
            if is_last_dim:
                assert key_new not in keys, "%s found in %s" % (key_new, keys)
                keys.append(key_new) 
                i+=1
            else:
                i = cls.fill_keys(keys, key_new, attrs_left[1:], i)
        assert len(keys)==i
        return i

    def pp_suffixes(self):
        return "\n".join(["%-10s= %s" % (k,self.suffixes[k]) for k in self.keys])


    # TODO: word_base -> word_base
    @classmethod
    def get_form(cls, word_base, lexem, suff, trace_vc_list=None, join_wf=True): 
        """
        >>> WordSuffixes.get_form("nositi", "nosi", "i")
        u'nosi'
        >>> WordSuffixes.get_form("nosi", "nosi", "i")
        u'nosiji'
        >>> WordSuffixes.get_form("poni", "poni", "i")
        u'poniji'

        >>> WordSuffixes.get_form("dummy", "", "")
        u''
        >>> WordSuffixes.get_form("", "", "")
        u''
        >>> WordSuffixes.get_form("", "", "0")
        u''

        >>> WordSuffixes.get_form("dummy", "črek", "je")
        u'\u010dre\u010de'
        >>> WordSuffixes.get_form("dummy", "žleg", "je")
        u'\u017ele\u017ee'
        >>> WordSuffixes.get_form("dummy", "hoda", "imo")
        u'hodajmo'

        is_suffix_base
        >>> WordSuffixes.get_form("", "", "im")
        u'im'

        join_wf = False then return base+suffix
        >>> WordSuffixes.get_form("dummy", "čpek", "ji", join_wf=False)
        (u'\u010dpe\u010d', u'i')
        >>> WordSuffixes.get_form("dummy", "pat", "tji", join_wf=False)
        (u'pat', u'ji')

        Test jotacije:
        >>> WordSuffixes.get_form("dummy", "čpek", "ji")
        u'\u010dpe\u010di'
        >>> WordSuffixes.get_form("dummy", "ćpet", "ji")
        u'\u0107pe\u0107i'
        
        Test remove duplicates:
        >>> WordSuffixes.get_form("dummy", "pat", "tji")
        u'patji'
        >>> WordSuffixes.get_form("dummy", "čpačk", "ji")
        u'\u010dpa\u010di'

        >>> WordSuffixes.get_form("radio", "radi", "a")
        u'radija'
        >>> vc_list = []
        >>> WordSuffixes.get_form("radio", "radi", "o", vc_list)
        u'radio'
        >>> vc_list
        []
        >>> WordSuffixes.get_form("radio", "radi", "ima", vc_list)
        u'radijima'
        >>> vc_list
        ['+I1']
        >>> vc_list = []
        >>> WordSuffixes.get_form("poni", "poni", "ima", vc_list)
        u'ponijima'
        >>> vc_list
        ['+I3']
        >>> WordSuffixes.get_form("poni", "poni", "")
        u'poni'
        >>> WordSuffixes.get_form("poni", "poni", "m")
        u'ponim'
        
        Sibilarization exceptions - names, go, ko
        >>> WordSuffixes.get_form("ginko", "gink", "%Sima")
        u'ginkima'
        >>> WordSuffixes.get_form("josko", "josk", "%Si")
        u'joski'
        >>> vc_list = []
        >>> WordSuffixes.get_form("rebro", "rebr", "%Aa", vc_list)
        u'rebara'
        >>> vc_list
        ['+A']

        >>> WordSuffixes.get_form("kupalište", "kupališt", "%Aa")
        u'kupali\u0161ta'
        >>> vc_list = []
        >>> WordSuffixes.get_form("mjesto", "mjest", "%Aa", trace_vc_list=vc_list)
        u'mjesta'
        >>> vc_list
        []

        J + M
        >>> vc_list = []
        >>> WordSuffixes.get_form("dummy", "šćlist", "je", vc_list)
        u'\u0161\u0107li\u0161\u0107e'
        >>> vc_list
        ['+J0', '+M']

        M
        >>> WordSuffixes.get_form("dummy", "šmisl", "ju")
        u'\u0161mi\u0161lju'

        Not good example: 
        >>> WordSuffixes.get_form("raditi", "radi", "ite")
        u'radiite'
        
        Good example: 
        >>> WordSuffixes.get_form("raditi", "rad", "ite")
        u'radite'
        """
        word_base = to_unicode(word_base).lower().strip()
        lexem = to_unicode(lexem).lower().strip()
        suff = to_unicode(suff).lower().strip()

        # if not word_base:
        #     assert not lexem
        #     if join_wf:
        #         return suff
        #     return u"", suff    

        vc = None
        lexem_curr = lexem
        base,suffix = "", ""
        if suff=="-":
            pass
        elif suff.startswith("!"):
            base = suff[1:]
            assert base
        else:
            if suff.startswith("$word_base"):
                lexem_curr = word_base
                suff = suff[len("$word_base"):]
            if suff.startswith("%"):
                if suff[1]=="-":
                    # TODO: %-A - remove  - not tested
                    vc_name=suff[1:3]
                    suff = suff[3:]
                else:
                    # apply
                    vc_name=suff[1]
                    suff = suff[2:]
                vc = WordSuffixes.get_vocal_change(vc_name)
                if vc_name.upper()=="S" and word_base[-2:] in ("go", "ko", "ha"): # TODO: and personal names too
                    vc = None
                # TODO: if this could be avoided?? apply_vc_a does this exception already
                elif vc_name.upper()=="A" and lexem[-2:] in cls.DONT_APPLY_VC_A_SUFF2:
                    #not (lexem[-1] not in AEIOU and lexem[-2] not in "aeiuo" and (
                    # and word_base[-2:] not in ("ko", "go")): - ginko 
                    vc = None
                    lexem = "%A"
            if suff=="0":
                base = lexem_curr
                suffix = ""
            elif suff.startswith("-"):
                num = ""
                for i, ch in enumerate(suff[1:]):
                    if not ch.isdigit():
                        break
                    num+=ch
                assert num
                num = -int(num)
                if i==0:
                    suffix = ""
                else:
                    assert suff[i+1:]
                    suffix = suff[i+1:]
                base = lexem_curr[:num]
            else:
                base = lexem_curr
                suffix = suff

            if vc:
                base, suffix = vc(base, suffix, trace_vc_list)
            if lexem not in ("s",): # for biti for S/3 s -> -1je base expires
                if not base and not suffix:
                    if join_wf:
                        return u""
                    return u"", u""
                assert base or suffix
                # NOTE: M is called for base+suffix inside J
                base, suffix = cls.apply_vc_L(base, suffix, trace_vc_list=trace_vc_list)
                base, suffix = cls.apply_vc_J(base, suffix, trace_vc_list=trace_vc_list)
                base, suffix = cls.apply_vc_D(base, suffix, trace_vc_list=trace_vc_list)
                # radio -> radi + a -> radij + a
                # TODO: change suffix??
                if base and base[-1] in "a" and suffix and suffix[0] in ("i",):
                    suffix = "j"+suffix[1:]
                    if not trace_vc_list is None:
                       trace_vc_list.append("+I4")
                elif word_base.endswith("io") and suffix and suffix[0] in "aeiu":
                    base = base+"j"
                    if not trace_vc_list is None:
                       trace_vc_list.append("+I1")
                # TODO: ovo je vjerojatno dio glasovne promjene - izmjena ie, ije, je, i
                # # piti -> pi + e -> pi+je, pi+u -> piju, pi+o -> pio (same)
                elif base[-1:]=="i" and suffix and suffix[0] in ("ue"):
                    base = base+"j"
                    if not trace_vc_list is None:
                       trace_vc_list.append("+I2")
                # poni -> poni + a -> ponij + a
                elif word_base==lexem and word_base.endswith("i") and suffix and suffix[0] in AEIOU: 
                    base = base+"j"
                    if not trace_vc_list is None:
                       trace_vc_list.append("+I3")
                    # TODO: trace_vc_list
                elif lexem and suffix and lexem[-1]==suffix:
                    suffix = suffix[1:]

                # TODO: this is not good solved!
                #    here is for:      radi + imo -> radimo 
                #    but not for: poni ima -> poni j ima    (this is change_D)
                # elif suffix and base[-1]==suffix[0]:
                #     suffix = suffix[1:]
        base, suffix = unicode(base), unicode(suffix)
        if join_wf:
            return base + suffix
        return base, suffix

    def get_forms(self, word_base, lexem=None, exceptions=None):
        if lexem is None:
            lexem = word_base
            if lexem.endswith("o"): # noun, m, radio -> radi, auto->aut
                lexem = lexem[:-1]
            elif lexem.endswith("e"): # noun, m, Hrvoje -> Hrvoj
                lexem = lexem[:-1]
            elif lexem.endswith("a"): # noun, F, srna -> srn
                lexem = lexem[:-1]
        elif lexem.startswith("%"):
            if lexem.upper().startswith("%A"):
                suffix = lexem[len("%A"):]
                lexem, suffix2 = self.remove_vc_A(word_base, suffix, trace_vc_list=None)
                assert suffix==suffix2
            else:
                raise Exception("invalid operator '%s' on word '%s'" % (lexem, word_base))
        if not isinstance(word_base, unicode):
            word_base = unicode(word_base, "utf-8")
        if not isinstance(lexem, unicode):
            lexem = unicode(lexem, "utf-8")
        
        words = set()
        forms = {}
        if exceptions:
            self.check_exceptions(self.keys, exceptions)
        used_excs = set()
        for k, s_list in self.suffixes.iteritems():
            assert k not in forms
            forms[k] = []
            if exceptions and k in exceptions:
                s_list = [_s.strip().lower() for _s in exceptions[k]]
                used_excs.add(k)
            for suff_item in s_list:
                f = self.get_form(word_base, lexem, suff_item)
                if f in forms[k]:
                    pass
                    # # TODO: ovo je moguće za slučaj %Si|i
                    # logger.info("form '%s' for '%s' already found in '%s' ('%s' in '%s')" % (
                    #     f, k, forms[k], suff_item, s_list))
                else:
                    forms[k].append(f)
                    words.add(f)
        if exceptions:
            all_excs = set(exceptions.keys())
            diff = all_excs - used_excs
            assert not diff, "Exceptions %s not applied / not found in '%s'" % (diff, self.suffixes.keys())

        return forms, words

    def get_forms_ordered(self, forms):
        assert isinstance(forms, dict), forms
        return [(k,forms[k]) for k in self.keys]

    def pp_forms(self, forms, encoding=None):
        assert isinstance(forms, dict), forms
        ret = "\n".join(["%-10s= %s" % (k,f) for k,f in self.get_forms_ordered(forms)])
        return ret

    def pp_forms_gender(self, word_base, lexem=None):
        assert self.attrs_ch_ordered[-1]==base.ATTR_GENDER, "Use this function for word types where gender is last attr (%s has %s)" % (self.word_type, self.attrs_ch_ordered)

        #s = SUFF_ADJ[key] 
        #print "\nPrinting: "+key+"\n"
        forms, words = self.get_forms(word_base=word_base, lexem=lexem)
        form_list = self.pp_forms(forms)
        ret = []
        for i, val in enumerate(form_list.split("\n")):
            if i%3==0:
                if i!=0:
                    ret.append(line)
                line = ""
            line+="%-41s " % val
        ret.append(line)
        return "\n".join(ret)

    # def pp_forms2(self, forms, attrs_ch_ordered):
    #     TODO: printout in different order - but problem is that key is not setup in original order: KeyError: 'M/S/N'
    #     keys = []
    #     i = self.fill_keys(keys, "", attrs_ch_ordered[:])
    #     assert set(attrs_ch_ordered)==set(self.attrs_ch_ordered), "%s must be the same as %s but can be in diff order" % (attrs_ch_ordered, self.attrs_ch_ordered)
    #     assert len(self.keys)==self.length, "%d!=%d" % (len(self.keys), self.length)
    #     return "\n".join(["%-10s= %s" % (k, forms[k]) for k in keys])


    def __str__(self):
        return "%s(%s, %d suffixes, based_on=%s)" % (self.name, "/".join([a.name for a in self.attrs_ch_ordered]), len(self.suffixes), ",".join([s.name for s in self.based_on]))

    def __repr__(self):
        return "%s at %X" % (str(self), id(self))
    
# moved from form.py

# class VocalChange(object):
#     pass
# 
# class NepostojanoAvocalChange(VocalChange):
#     TYPES = { "NM"  : "N.M/S/N|M/P/G", 
#               "NF"  : "N.F/P/G", 
#               "ADJ" : "ADJ.NEO/M/S/N", 
#               "SUB" : "SUB.M/S/N"
#             }
#     def __init__(self, word_type, type):
#         assert type in self.TYPES
#         self.word_type = self.TYPES[type].split(".")[0]
#         assert word_type == self.word_type
# 
#     def get_form(self, lexem, suffix, form, attrs):
#         if self.type==("N.M/(S/N)|(P|G)":
#         elif self.type==("N.F/P/G")
#         elif self.type, "ADJ.NEO/M/S/N", "SUB.M/S/N")
#         # find last two suglasnik - a must be between them - remove it
#         return form

# TODO: should i drop this class in favor to chang.word class?
#       i assume so
class WordForms(object):
    def __init__(self, word_type_str, word_base, lexem, 
                 attrs_same_values, 
                 suffixes, 
                 attr_extra=None):
        """ word_base is base word form (e.g. for verb infinitive), and lexem is base part of the word
            that is not changed (e.g. for word pričati is prič, then you add suffixes to 
            create new forms of the word
            for attr_fix_values - value * means - "applied for all"
            """
        assert base.is_word_type_registred(word_type_str), "Unknown %s word_type" % word_type_str
        # self.vocal_changes = vocal_changes
        # if self.vocal_changes:
        #     for vc in self.vocal_changes:
        #         assert isinstance(vc, VocalChange)
        self.word_type=base.get_word_type(word_type_str)
        self.attr_extra=attr_extra
        assert isinstance(suffixes, WordSuffixes)
        self.suffixes = suffixes
        self.wt_attrs_all = self.word_type.attrs
        self.wt_attrs_ch  = self.word_type.attrs_ch
        # fake V -> VA
        if self.suffixes._name.startswith("V##VA_"):
            self.wt_attrs_all = self.wt_attrs_all[:-1]+[base.ATTR_GENDER]
            self.wt_attrs_ch  = self.wt_attrs_ch[:-1] +[base.ATTR_GENDER]
        self.attrs_same_values = []
        assert len(attrs_same_values)<=len(self.wt_attrs_all)
        for attr_value, attr in zip(attrs_same_values, self.wt_attrs_all):
            assert attr_value in attr.values, "%s - %s not in values %s" % (
                                                    attr, attr_value, attr.values)
            self.attrs_same_values.append((attr, attr_value))
        self.attrs_diff_values = []
        attrs_left = self.wt_attrs_all[len(attrs_same_values):]
        assert len(attrs_left)==len(self.suffixes.attrs_ch_ordered), "len diff %s != %s" % (attrs_left, self.suffixes.attrs_ch_ordered)
        for i, attr in enumerate(attrs_left):
            assert attr in self.wt_attrs_ch
            assert self.suffixes.attrs_ch_ordered[i]==attr, "%s %s %s" % (self.suffixes, self.suffixes.attrs_ch_ordered[i],attr)
            self.attrs_diff_values.append(attr)
        assert len(self.attrs_diff_values)+len(self.attrs_same_values)==len(self.wt_attrs_all)

        assert self.wt_attrs_ch, "use this class for changable word types, %s" % self.word_type
        if not lexem:
            #if word_type_str=="V":
            #    lexem, klass = get_lexem_and_klass(word_type_str, word_base)
            #else:
            raise Exception("lexem for word %s/%s is empty" % (word_type_str, word_base))
        self.word_base, self.lexem = word_base.strip().lower(), lexem.strip().lower()
        if not isinstance(self.word_base, unicode):
            # TODO: replace with to_unicode
            self.word_base = unicode(self.word_base, "utf-8")
        if not isinstance(self.lexem, unicode):
            self.lexem = unicode(self.lexem, "utf-8")
        # NOTE: Doesn't seem too useful
        #if word_base_lexem_match:
        #    assert self.word_base.startswith(self.lexem), "%s word_base should begin with lexem %s" % (self.word_base, self.lexem)
        self.forms, self.words = self.suffixes.get_forms(self.word_base, self.lexem)
        self.forms_ordered = self.suffixes.get_forms_ordered(self.forms)
        # if word_base_lexem_match:
        #     assert self.word_base==self.forms_ordered[0][1][0], "word_base '%s' should be same as very first form '%s'" % (self.word_base, self.forms_ordered[0][1][0])

    def pp_suffixes(self, encoding=None):
        ret = self.suffixes.pp_suffixes()
        return ret

    def pp_forms(self, encoding=None):
        ret = self.suffixes.pp_forms(self.forms)
        # TODO: this doesn't work
        # if encoding:
        #     ret = ret.decode(encoding)
        return ret

    def get_forms_ordered(self):
        return self.suffixes.get_forms_ordered(self.forms)

    def __str__(self):
        ret = u"%s(%s/%s/%s)=%d/%d/%d" % (self.word_type.name, self.word_base, self.lexem, self.suffixes, len(self.attrs_diff_values), len(self.attrs_same_values), len(self.forms))
        return codecs.encode(ret, "utf-8")

    def __repr__(self):
        return "%s at %X" % (str(self), id(self))

# TODO: drop this class or merge with ChangeableWord
#       it is used in base.py::ChangeableWordType.add_word
#       which is used in pronouns and verbs for adding std.words
#       change this to new ChangeableWord
class ChangeableWordOld(object):

    def __init__(self, word_type_str, word_base, attrs_fix=()):
        self.word_type=base.get_word_type(word_type_str)
        self.word_type_str, self.word_base = word_type_str, word_base
        # TODO: not filled, not checked with wt, should be used in nouns (gender), should be assigned to suffixes
        self.attrs_fix = attrs_fix
        self.forms = {}

    # TODO: this is bad - 3 functions - only one is nice - guess which?
    def get_all_forms(self):
        """ returns all forms in (key, forms) ordered by key"""
        return [(k, self.forms[k]) for k in sorted(self.forms.keys())]

    def get_forms(self, key):
        # if self.word_base=="biti":
        #     pritn self.forms.keys()
        #     import pdb;pdb.set_trace() 
        key = self.word_type.adjust_key(key, self.forms.keys())
        return self.forms[key]

    # def get_forms_ordered(self, forms):
    #     assert isinstance(forms, dict), forms
    #     return [(k,forms[k]) for k in self.keys]

    # def get_suffixes(self, key):
    #     key = self.word_type.adjust_key(key, self.forms.keys())
    #     return self.forms[key].suffixes

    def add_forms(self, lexem, attrs_same_values, suffixes, 
                  attr_extra=""): #, word_type_conv_str=""):
        # TODO: for this wt check if suffixes are ok for this wt and attrs_same_values, like this:
        #       take care that for VA - suffixes are valid also for V too (see verbs VA)
        #       suffixes in self.word_type.get_valid_suffixes(attrs_same_value)
        if isinstance(attrs_same_values, str):
            attrs_same_values = attrs_same_values.split("/")
        assert isinstance(attrs_same_values, (list, tuple)), attrs_same_values
         
        # if word_type_conv_str:
        #     word_type_str_param = word_type_conv_str
        # else:
        word_type_str_param = self.word_type_str          

        key = "%s#%s#%s" % (word_type_str_param, "/".join([v for v in attrs_same_values]), 
                             attr_extra)
        assert key not in self.forms.keys(), "%s in %s" % (key, self.forms.keys())
        self.forms[key]=WordForms(    word_type_str      = word_type_str_param 
                                    , word_base              = self.word_base
                                    , lexem              = lexem
                                    , attrs_same_values  = attrs_same_values
                                    , suffixes           = suffixes
                                    , attr_extra         = attr_extra)

        if self.word_type.code=="V":
            if attrs_same_values[0]=="PRE":
                lexem = self.forms[key].lexem
                # glagolski prilog sadašnji - particip prezenta - only verbs - present for S/3 needed""" 
                if self.word_base=="htjeti":
                    v_adv_pre = u"hoteći"
                elif self.word_base=="biti":
                    v_adv_pre = u"budući"
                else:
                    v_adv_pre = self.forms[key].forms["P/3"][0] + u'\u0107i'
                    v_adv_pre = self.forms[key].forms["P/3"][0] + u'\u0107i'
                key = "%s#%s#%s" % (word_type_str_param, "ADV_PRE", "")
                self.forms[key]=v_adv_pre

                # glagolski prilog prošli - particip perfekta - only verbs - infinitiv needed
                if lexem[-1] in AEIOU:
                    v_adv_pas = lexem + u"vši"
                else:
                    v_adv_pas = lexem + u"avši"
                key = "%s#%s#%s" % (word_type_str_param, "ADV_PAS", "")
                self.forms[key]=v_adv_pas

    # def get_V_ADV_PRE(self):
    #     """ glagolski prilog sadašnji - particip prezenta - only verbs - present for S/3 needed""" 
    #     assert self.word_type.code=="V"
    #     if self.word_base=="htjeti":
    #         return u"hoteći"
    #     if self.word_base=="biti":
    #         return u"budući"
    #     # TODO: No better way ...
    #     assert self.suffixes.name.find("PRE")>=0, "%s should have present suffixes - now in %s" % (self.word_base, self.suffixes.name) 
    #     return self.forms["P/3"][0] + u'\u0107i'

    # def get_V_ADV_PAS(self):
    #     """ glagolski prilog prošli - particip perfekta - only verbs - infinitiv needed"""
    #     assert self.word_type.code=="V"
    #     if self.lexem[-1] in AEIOU:
    #         return self.lexem + u"vši"
    #     return self.lexem + u"avši"

class ChangeableWordBase(object):
    """ abstract class - must be inherited
    """

    @classmethod
    def __key_helper(cls, item):
        if isinstance(item, tuple):
            param_name, key_name = item
        else:
            param_name = item
            key_name=param_name[0]
        key_name = key_name.upper()
        return key_name, param_name

    @classmethod
    def key2params(cls, key):
        param_name_list = cls.PARAM_NAME_LIST
        if not param_name_list:
            raise NotImplementedError("probably you should define PARAM_NAME_LIST in child class")

        # adj   ["apply_vc_a", ("has_neo", "n"), ("has_com", "c"), ("com_wp1_suff", "s")]
        # nouns ["decl", "apply_vc_a", "gender", "ext", "spec"]
        # verbs ["ext"]

        params_init = {}
        key_dict = {}
        key_name_dict = dict([cls.__key_helper(item) for item in param_name_list])
        # import pdb;pdb.set_trace() 
        for item in key.split("/"):
            val, key_name = item[:-1], item[-1]
            assert len(val)>=1, key
            assert key_name in key_name_dict, key
            param_name = key_name_dict.pop(key_name)
            assert param_name not in params_init
            if val=="$":
                value = None
            elif val=="+":
                value = True
            elif val=="-":
                value = False
            # elif val.isdigit():
            #     value = int(val)
            elif val=="#":
                value = ""
            else:
                value = val
            params_init[param_name]=value
        assert not key_name_dict, key_name_dict
        assert params_init
        return params_init

    @classmethod
    def params2key(cls, params_init):
        param_name_list = cls.PARAM_NAME_LIST
        if not param_name_list:
            raise NotImplementedError("probably you should impl. this class in child class")
        key = []
        key_names = {}
        params_init = params_init.copy()
        for item in param_name_list:
            key_name, param_name = cls.__key_helper(item)
            assert key_name not in key_names, key_name
            value = params_init.pop(param_name, None)
            if value is None:
                val = "$"
            else:
                if isinstance(value, bool):
                    val = "+" if value else "-"
                elif isinstance(value, int):
                    val = "%s" % value
                else:
                    assert isinstance(value, basestring), type(value)
                    # assert value.islower()
                    val = value if value else "#"
            key.append("%s%s" % (val, key_name))
            key_names[key_name]=val
        assert not params_init, params_init
        return "/".join(key)


    def __init__(self, word_type, word_base, attr_vals_fix, is_suffix, 
                 accept_attr_none=False, status="T"):
        """ other attrs are word_type based so they must exist in 
            inherited classes
        """
        self._id_saved = None
        self._is_rejected = None
        if isinstance(word_type, basestring):
            word_type=base.get_word_type(word_type)
        else:
            assert isinstance(word_type, base.ChangeableWordType)
        self.word_type, self.word_base = word_type, to_unicode(word_base)
        self.attr_vals_fix, self.is_suffix = attr_vals_fix, is_suffix
        self.status = status
        assert self.status in base.STATUS_LIST
        assert isinstance(attr_vals_fix, (list, tuple))
        assert len(self.word_type.attrs_fix)==len(self.attr_vals_fix)
        for attr_val, attr in zip(self.attr_vals_fix, self.word_type.attrs_fix):
            if accept_attr_none and attr_val is None:
                pass
            else:
                assert attr_val in attr.values
            assert not hasattr(self, attr.code)
            setattr(self, attr.code, attr_val)

        # self.similar_words[word_obj.key]=(word_obj, len(has_both_stats), len(has_both_forms))
        self.similar_words = {}
        # self.forms = {}

    def init_forms_common(self):
        self._forms_flat = []
        self._forms_stats = {}

        self._sum_freq = None
        self._sum_freq_exists = None
        self._forms_exists_set = None
        self._forms_set = None

        for attr_vals in self.attr_values:
            key = "/".join(attr_vals)
            if key not in self._forms:
                import pdb;pdb.set_trace() 
                assert False
            wf_list = self._forms[key]
            self._forms_flat.append((key,wf_list))
            for wf in wf_list:
                if wf not in self._forms_stats:
                    if wf: # don't store empty ...
                        assert isinstance(wf, basestring), wf
                        self._forms_stats[wf] = (0, None) # freq - later will be some object with weights etc.

    def set_form_freq(self, wf, freq, word_id):
        self.forms_stats[wf]=(freq, word_id)
        self._sum_freq = None
        self._sum_freq_exists = None
        self._forms_exists_set = None
        self._forms_set = None

    def get_forms_freq_sum(self):
        if self._sum_freq is None:
            self._sum_freq = sum([item[0] for wf, item in self.forms_stats.iteritems()])
        return self._sum_freq

    def get_forms_exists_set(self):
        if self._forms_exists_set is None:
            self._forms_exists_set = set([wf for wf, item in self.forms_stats.iteritems() if item[0]])
        return self._forms_exists_set

    def get_forms_set(self):
        if self._forms_set is None:
            self._forms_set = set([wf for wf in self.forms_stats.keys()])
        return self._forms_set

    def get_forms_exists_freq_sum(self):
        if self._sum_freq_exists is None:
            self._sum_freq_exists = sum([1 for wf, item in self.forms_stats.iteritems() if item[0]])
        return self._sum_freq_exists

    def is_better_than(self, other):
        """ New logic word_forms intersection/diff simplified this task
            returns True if self is better, False if other is better, 
            other if they are the same 
        """
        is_better = None
        # if  (   unicode("brbljalo", "utf-8") in (self.word_base, )  # other.word_base
        #     and unicode("brbljalo", "utf-8") in (other.word_base,)): # self.word_base, 
        #      import pdb;pdb.set_trace() 
        # if  (    unicode("brbljavac", "utf-8") in (self.word_base, other.word_base)
        #      and unicode("brbljavc", "utf-8")  in (self.word_base, other.word_base)):
        #      import pdb;pdb.set_trace() 

        # Take one with WORD_BASE EXISTS
        if is_better is None:
            has_base_this  = self.forms_stats[self.word_base][0]>0
            has_base_other = other.forms_stats[other.word_base][0]>0
            if has_base_this!=has_base_other:
                if has_base_this:
                    is_better=True
                else:
                    is_better=False
            elif has_base_this:
                assert has_base_other
                # Both have base exists - take one with WORD_BASE more frequent
                freq_base_diff  = (self.forms_stats[self.word_base][0] - 
                                   other.forms_stats[other.word_base][0])
                if freq_base_diff>0:
                    is_better = True
                elif freq_base_diff<0:
                    is_better = False


        # TODO: take with better SRI 
        #           - the one that is more characteristic and more specific
        #           - that has word_base found
        #           - in some cases ADJ/N, ADJ/ADJ etc. there should be specific rules
        #       in cases when there is only one or few - take better ??
        #       -  1/    1 -> brendirani           (u'ADJ-od3_iji_-_ANI-anu-0') 1/brendiranu
        #       +  1/    1 -> brendirana           (u'N-mj_F_ANA-anu-0') 1/brendiranu
        # Take with longer SRI.WTS.suff_value
        if is_better is None and self.sri and other.sri:
            suff_len_diff = len(self.sri.wts.suff_value)-len(other.sri.wts.suff_value)
            # NOTE: min diff is 2 chars
            if suff_len_diff>0: # 1
                is_better = True
            elif suff_len_diff<0: # -1
                is_better = False

        # Take one with less forms_flat
        if is_better is None:
            form_len_diff = len(self.forms_flat)-len(other.forms_flat)
            if form_len_diff>0:
                is_better = False
            elif form_len_diff<0:
                is_better = True

        # if everything fails - take less by key (order by)
        if is_better is None:
            key1 = self._get_key()
            key2 = other._get_key()
            assert key1!=key2
            if key1<key2:
                is_better = True
            else:
                assert key1>key2
                is_better = False

        # should be something
        assert is_better is not None

        return is_better

    def _get_params_key(self):
        # NOTE: what if it changed in the meantime 
        if not hasattr(self, "_params_key"):
            self._params_key = self.params2key(self.params_init)
        return self._params_key
    params_key = property(_get_params_key)
    

    def _get_key(self):
        # NOTE: when Verb then lexem is pair of lexems (pre, inf)
        # lexem = self.word_lexem
        if not hasattr(self, "_key"):
            self._key = "%s|%s|%s" % (self.word_type.code, self.word_base, 
                                 # |%s|%s lexem, self.sri.suff_value if self.sri else "$",
                                 self.params_key)
        return self._key
    key = property(_get_key)

    def __getitem__(self, key):
        raise NotImplementedError("currently must be implemented in inherited class")
        return "%s,demo" % key

    def __str__(self):
        return "W(%s=%s)" % (repr(self.word_base), self.word_type.code)

    def __repr__(self):
        return "%s at %0X" % (self, id(self))

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.forms_flat[key]
        return self.forms[key]

    def __iter__(self):
        for k,v in self.forms_flat:
            yield k,v

    ## def get_all_forms(self):
    ##     """ returns all forms in (key, forms) ordered by key"""
    ##     return [(k, self._forms[k]) for k in sorted(self._forms.keys())]

# ----------------------------------------

class WordTypeSuffix(object):
    # TODO: put this in some common class - e.g. morphs
    FREQ_TYPE = {0 : "very rare",
                 -1: "unknown freq",
                 1 : "not frequent",
                 2 : "frequent",
                 3 : "very frequent"}

    # TODO: from which word_type can be made
    def __init__(self, word_type, attrs_fix, suff_value, freq_type, group, desc="", examples="",
                 vc_list=None, register=True, base_ends_aeiou=None, **kwargs):
        self.word_type, self.suff_value, self.attrs_fix, self.freq_type, self.group, self.desc = (
             word_type,      suff_value,      attrs_fix,      freq_type,      group,      desc)
        if kwargs:
            for name, val in kwargs.iteritems():
                setattr(self, name, val)

        self.base_ends_aeiou = base_ends_aeiou
        # TODO: maybe something like this can be done 
        #       if suff_value[0] in AEIOU: then what??

        self.vc_list, self.register = vc_list, register

        self.is_blank=(self.group=="##")
        self.examples = []
        if not self.is_blank:
            assert self.suff_value
        self.is_base = (self.suff_value=="$BASE$")
        if self.is_base:
            self.suff_value = ""
        else:
            assert examples
            for e in examples.split(","):
                e = to_unicode(e.strip().lower())
                assert e.isalpha(), e
                self.examples.append(e)
        # vocal changes list - e.g. %s
        assert isinstance(self.suff_value, basestring), self.suff_value
        assert self.suff_value.find("|")<0, self.suff_value
        self.suff_value = to_unicode(self.suff_value).lower()
        #self.suff_value = [to_unicode(s) for s in self.suff_value.split("|")]
        #assert len(self.suff_value) in (1,2,3), self.suff_value
        if self.vc_list:
            assert self.suff_value[0].lower() not in AEIOU, self.suff_value
            if isinstance(self.vc_list, basestring):
                self.vc_list = self.vc_list.upper().split("|")
            for vc in self.vc_list:
                assert vc in WordSuffixes.get_vc_dict().keys(), vc
                assert vc not in "A", vc

        self.group = to_unicode(self.group)
        self.desc = to_unicode(self.desc)
        assert self.freq_type in self.FREQ_TYPE

        # check attrs_fix
        wt_codes = [a.code for a in self.word_type.attrs_fix]
        wt_not_here=set(wt_codes) - set(self.attrs_fix.keys())
        assert not wt_not_here, wt_not_here
        here_not_wt=set(self.attrs_fix.keys())-set(wt_codes)
        assert not here_not_wt, here_not_wt
        for attr in self.word_type.attrs_fix:
            assert attr.code in self.attrs_fix, "%s not in %s" % (attr.code, self.attrs_fix.keys())
            attr_value = self.attrs_fix[attr.code]
            if attr_value!="?": # ? indicates that this is unknown by the suffix
                assert attr_value in attr.values, "%s not in %s" % (attr_value, attr.values)

        if self.word_type.attrs_fix:
            attr_code = "/".join([self.attrs_fix[a.code] for a in self.word_type.attrs_fix])
        else:
            attr_code = "-"
        self.code = (self.group +"_"+attr_code
                     +"_"+self.suff_value.upper())

    def __str__(self):
        """
        >>> from nouns import NOUNS
        >>> print WordTypeSuffix(NOUNS, {"GEN":"F"}, "s", 0, "CD1", "test", examples="example", register=False)
        WTS(wt=N,cd=u'CD1_F_S',list=u's',freq=very rare)
        >>> print WordTypeSuffix(NOUNS, {"GEN":"M"}, "%ac", 3, "CD1", examples="example", register=False)
        WTS(wt=N,cd=u'CD1_M_%AC',list=u'%ac',freq=very frequent)
        >>> print WordTypeSuffix(NOUNS, {"GEN":"M"}, unicode("ač", "utf-8"), 2, "VR", examples="example", register=False)
        WTS(wt=N,cd=u'VR_M_A\u010c',list=u'a\u010d',freq=frequent)
        >>> print WordTypeSuffix(NOUNS, {"GEN":"M"}, unicode("če", "utf-8"), 2, "VR", examples="example", vc_list="S|J", register=False)
        WTS(wt=N,cd=u'VR_M_\u010cE',list=u'\u010de',freq=frequent)
        """
        vc_spec = ""
        if self.vc_list:
            vc_spec = ",vc_list=%s" % "|".join(self.vc_list)

        return "WTS(wt=%s,cd=%s,list=%s,freq=%s%s)" % (self.word_type.code, 
                repr(self.code), repr(self.suff_value),
                self.FREQ_TYPE[self.freq_type], "")

    def __repr__(self):
        return "%s at %0X" % (str(self), id(self))

    def add_forms(self, wts_suff_list):
        assert self.register
        for word_obj, suff_key, ordnr, suff_value in wts_suff_list:
            if not suff_value:
                continue
            elif suff_value.find("$")>=0:
                continue
            # suff_key = suff_value
            ordnr = 0
            # TODO: diff vocal changes apply - vc_list - how to do this - for now replace with ""
            if "%a" in suff_value.lower():
                assert word_obj.apply_vc_a==self.apply_vc_a
                # with_this = "a" if word_obj.apply_vc_a else ""
                with_this = ""
                suff_value = suff_value.replace("%a", with_this).replace("%A", with_this)
                #if split_by_last_AEIOU(suff)[1]!="":
                #    suff4filter = suff4filter.replace("%a", "")
                #else:
                #    suff4filter = suff4filter.replace("%a", "a")
            if "%s" in suff_value.lower():
                #ch_next = suff_value[suff_value.lower().find("%s")+len("%s")]
                #if ch_next=="i":
                suff_value = suff_value.replace("%s", "").replace("%S", "")
            if "%p" in suff_value.lower():
                #ch_next = suff_value[suff_value.lower().find("%s")+len("%s")]
                #if ch_next in ("i", "e", "<nepostojano-a>"):
                suff_value = suff_value.replace("%p", "").replace("%P", "")
            if suff_value=="-":
                suff_value = ""
            suff_value = suff_value.replace("0", "")
            # TODO: what with this
            # #("$word_base", ""),
            # #("$__lexem__$", ""),
            for ch in "%$_&-?":
                if suff_value.find(ch)>=0:
                    assert False, suff_value
            if suff_value:
                get_suff_registry().add_suffix(self, word_obj, suff_key, ordnr, suff_value)
            
#---------------------------------------- 
        
class SuffixRegistryItem(object):
    def __init__(self, wts, word_obj, suff_key, ordnr, suff_value):
        assert isinstance(wts, WordTypeSuffix), word_type
        assert isinstance(word_obj, ChangeableWordBase), word_obj
        self.word_type = word_obj.word_type
        self.wts, self.word_obj, self.suff_key, self.ordnr, self.suff_value = wts, word_obj, suff_key, ordnr, suff_value
        self.key = "%s-%s-%s-%d" % (self.word_type.code, getattr(self.wts, "code", "-"), self.suff_value, self.ordnr)

    def __str__(self):
        return "SRI(%s, %s)" % (repr(self.suff_value), repr(self.key))

    def __repr__(self):
        return "%s at %0X" % (str(self), id(self))

#---------------------------------------- 

class SuffixRegistry(object):
    """ TODO: there should be distinction between suffixrule/suffixset/suffixes/suffix_list and 
              one suffix e.g. "ima"
        TODO: make affix also
    """
    def __init__(self):
        self.suffix_dict = {}
        self.suffix_dict_unique = {}

    def add_suffix(self, wts, word_obj, suff_key, ordnr, suff_value):
        """ suff_value wts can be None - when base form
        """
        item = SuffixRegistryItem(wts, word_obj, suff_key, ordnr, suff_value)
        if item.key in self.suffix_dict_unique:
            return
        self.suffix_dict_unique[item.key]=item
        # TODO: values should be by word_type - maybe some "new" class with counter?
        self._add_item(item.suff_value, item.word_type.code, item)

    def _add_item(self, suff_value, wt_code, item):
        if suff_value not in self.suffix_dict:
            self.suffix_dict[suff_value]=[]
        self.suffix_dict[suff_value].append(item)


    def __iter__(self):
        """ 
        >>> x = SuffixRegistry()
        >>> x._add_item("suff1", "N", 1)
        >>> x._add_item("suff1", "V", 2)
        >>> x._add_item("suff1", "N", 3)
        >>> x._add_item("suff1", "N", 4)
        >>> x._add_item("suf2", "N", 5)
        >>> x._add_item("suf2", "N", 6)
        >>> x._add_item("suf3", "V", 6)
        >>> x._add_item("suf3", "A", 7)
        >>> x._add_item("suf3", "N", 8)
        >>> x._add_item("suf4", "N", 9)
        >>> x._add_item("suf4", "A", 10)
        >>> x._add_item("su5", "A", 10)
        >>> x._add_item("suffix6", "A", 10)
        >>> x._add_item("suffix6", "N", 10)
        >>> x._add_item("suffix6", "V", 10)
        >>> x # doctest: +ELLIPSIS
        SR(6 suffixes, 0 SRI objects) at ...
        >>> list(x) # doctest: +NORMALIZE_WHITESPACE
        [('suffix6', [10, 10, 10]), 
         ('suff1', [1, 2, 3, 4]), 
         ('suf2', [5, 6]), 
         ('suf4', [9, 10]), 
         ('suf3', [6, 7, 8]), 
         ('su5', [10])]
        """
        def sort_fun(item_tuple):
            """ item_tuple = ('suf2', {'N': [5, 6]}) 
            sort by 
                - longest suffix (len(suff) asc), 
                - shortest number of sri_list (len sri desc), 
                - suff_value asc
            """
            #return "%04d_%02d" % (len(item_tuple[0]), 10-len(item_tuple[1]))
            return "%04d_%04d_%s" % (100-len(item_tuple[0]), len(item_tuple[1]), item_tuple[0])

        for suff_value, item in sorted(self.suffix_dict.iteritems(), key=sort_fun):
            yield suff_value, item

    def __str__(self):
        return "SR(%d suffixes, %d SRI objects)" % (len(self.suffix_dict), 
                                                         #", ".join(["%s=%d" % (st, len(self.suffix_dict_type[st])) for st in self.suffix_dict_type]),
                                                         len(self.suffix_dict_unique))
    def __repr__(self):
        return "%s at %0X" % (str(self), id(self))

# -------------------------
# global object - registry of all suffixes
# -------------------------
_suff_registry = None
_suff_registry_all = False

def get_suff_registry(init_all=False, load=False, store=False):
    import cPickle as pickle, os

    global _suff_registry, _suff_registry_all

    def get_fname():
        return os.path.join(os.path.dirname(__file__), ".suff_registry.pickle")

    if not _suff_registry:
        if load and not os.path.exists(get_fname()):
            print "%s not existing, will be created and saved" % (get_fname())
            load = False
            init_all = True
            store = True
        if load:
            assert init_all, not store
            fin = open(get_fname(), 'rb')
            _suff_registry = pickle.load(fin)
            _suff_registry_all = True

        elif init_all:
            from adjectives     import ADJECTIVES
            from nouns          import NOUNS    
            from verbs          import VERBS   

            _suff_registry = SuffixRegistry()

            ADJECTIVES.init_wts_forms()
            NOUNS.init_wts_forms()
            VERBS.init_wts_forms()

            _suff_registry_all = True
        else:
            _suff_registry = SuffixRegistry()
    else:
        if init_all:
            pass
            # this raises err in py tests: assert _suff_registry_all
        else:
            assert not load

    assert _suff_registry

    if store:
        assert _suff_registry_all
        # assert init_all
        fout = open(get_fname(), 'wb')
        pickle.dump(_suff_registry, fout, protocol=2)

    return _suff_registry


#forms, words = SUFF_ZAM_OS["P/3M"].get_forms("one", "njim")
#forms, words = SUFF_ZAM_OS["P/3M"].get_forms("ona", "njim")
# print SUFF_ZAM_OS["P/3M"].pp_forms(forms)

# print SUFF_ZAM_MOJ.pp_suffixes()
# forms, words = SUFF_ZAM_MOJ.get_forms("moj")
# print SUFF_ZAM_MOJ.pp_forms(forms)
# forms, words = SUFF_ZAM_MOJ.get_forms("tvoj")
# print SUFF_ZAM_MOJ.pp_forms(forms)

def print_all_vc_changes():
    """
    TODO: this is work in progress - doesn't fetch all ... and fetches on wrong place 
    """
    started = datetime.datetime.now()
    vc_transforms = {}
    z = cnt_all = 0
    #for left_ch3 in ALPHABET_LIST: 
    #    print "- %s -" % left_ch3
    for left_ch2 in ALPHABET_LIST: 
        # if left_ch3==left_ch2:
        #     continue
        # print "- %s -" % left_ch2
        for left_ch1 in ALPHABET_LIST: 
            if left_ch2==left_ch1:
                continue
            #left_op = left_ch3+left_ch2+left_ch1
            left_op = left_ch2+left_ch1
            for right_op in ALPHABET_LIST: 
                cnt_all += 1
                res_no_vc = left_op + right_op
                any_vocals = sum([1 for ch in res_no_vc if ch in (AEIOU+"r")])
                if not any_vocals:
                    continue
                vc_list = []
                res_with_vc = WordSuffixes.get_form("dummy", left_op, right_op+"|||", vc_list)

                res_with_vc = uni_prepare(res_with_vc.replace("|",""))
                res_no_vc = uni_prepare(res_no_vc)

                if res_no_vc!=res_with_vc:
                    left_op = uni_prepare(left_op)
                    right_op = uni_prepare(right_op)
                    # abc -> abč
                    # c -> č
                    for ind, left_ch in enumerate(left_op):
                        if ind>=len(res_with_vc)-1:
                            break
                        if left_ch!=res_with_vc[ind]:
                            break
                    new_left = left_op[ind:]
                    if not new_left or (new_left==right_op):
                        continue
                    new_res = uni_revert(res_with_vc[ind:])
                    new_left = uni_revert(new_left)
                    right_op = uni_revert(right_op)
                    key = "%s+%s" % (new_left, right_op)
                    #, new_res)
                    if key not in vc_transforms.keys():
                        vc_transforms[key]=new_res
                        print "(%s+%s=%s != %s)  %s+%s=%s , vc=%s" % (left_op, right_op, res_with_vc, res_no_vc, 
                                                                      new_left, right_op, new_res, vc_list)
                        z+=1
                        # if z>2000:
                        #     raise Exception("stop")
                    else:
                        # TODO: count them
                        assert vc_transforms[key]==new_res, "%s : %s!=%s" % (key, vc_transforms[key], new_res)
    print z
    ended = datetime.datetime.now()
    print ended - started

    #print repr(uni_revert(ch)),


def test():
    # TODO: work in progress ... not done well ... only some catched
    # print_all_vc_changes()
    # (ab+j=ab& != abj)  b+j=blj , vc=['+J1']
    # (ac+j=ač != acj)  c+j=č , vc=['+J0']
    # (ad+j=ađ != adj)  d+j=đ , vc=['+J0']
    # (ag+j=až != agj)  g+j=ž , vc=['+J0']
    # (ah+j=aš != ahj)  h+j=š , vc=['+J0']
    # (ai+e=aije != aie)  i+e=ije , vc=['+I2']
    # (ai+u=aiju != aiu)  i+u=iju , vc=['+I2']
    # ...
    # return
    print "%s: running doctests" % __name__
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    test()

        #     else:
        #         # if same or similar sized then take one which come first (order) - we must have something
        #         if self.sri.suff_value<other.sri.suff_value:
        #             is_better = True
        #         else:
        #             is_better = False
        # sum_freq_this = self.get_forms_exists_freq_sum()
        # sum_freq_other = other.get_forms_exists_freq_sum()

        # TODO: use this too
        # sum_freq_this = self.get_forms_freq_sum()
        # sum_freq_other = other.get_forms_freq_sum()

        # if unicode("brušen", "utf-8") in (self.word_base, other.word_base) and unicode("brušeni", "utf-8") in (self.word_base, other.word_base):
        #     import pdb;pdb.set_trace() 

        # if sum_freq_this>sum_freq_other:
        #     is_better = True
        # elif sum_freq_this<sum_freq_other:
        #     is_better = False
        # else:
        #     # TODO: this is to be checked - sri check and has_base check can conflict
        #     #       you never know what to prefer - maybe some pondering ...
        # if (self.word_type.code==other.word_type.code 
        #     and self.word_type.code=="ADJ"):
        #     and "i" in (self.word_base[-1], other.word_base[-1])

        # brušen BETTER brušeni - Brušen is better - neo
        # if wb_test[-1] in AEIOU:
        #     wb_test = wb_test[:-1]
        # wb_test_applied = _remove_vc_a(wb_test)
        # if wb_test!=wb_test_applied:

        # if is_better is None and (
        #     self.word_type.code==other.word_type.code 
        #     and self.word_type.code=="ADJ" 
        #     and "i" in (self.word_base[-1], other.word_base[-1])
        #     and (self.word_base[:-2].startswith(other.word_base[:-2])
        #          or 
        #          other.word_base[:-2].startswith(self.word_base[:-2]))
        #     ):
        #     if self.word_base[-1]=="i":
        #         is_better=False
        #     else:
        #         assert other.word_base[-1]=="i"
        #         is_better=True



