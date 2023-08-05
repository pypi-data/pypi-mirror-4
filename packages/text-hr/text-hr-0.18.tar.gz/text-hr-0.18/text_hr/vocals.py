# coding=utf-8
# Croatian voices? - glasovi
# useful doctest
# doctest:+ELLIPSIS
# doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
# PREMA: Gramatici hrvatskog jezika - Težak, Babić, str. 47-56, tvrdnje 76-101
# TODO: glasovne promjene

# nepostojano_a
# nepostojano_e
# navezak
# vokalizacija
# palatalizacija
# sibilarizacija
# jotacija
# jedn_sumn_po_zvucnosti
# jedn_glas_po_mjestu_tvorbe
# gubljenje_suglasnika
# smjenjivanje_ie_je_e_i
# i_duljenje_kratkog_je
# ii_kracenje_sloga_s_dvoglasn
# iii_sugl_skupina_sa_r
# iv_ostala_pravila
"""
>>> OTVORNICI # doctest:+ELLIPSIS
Category OTVORNICI (a,e,i,ie,o,u) at ...

>>> ZVON_USNI_PRIBLIZNICI # doctest:+ELLIPSIS
Category ZVON_USNI_PRIBLIZNICI (j,v) at ...

>>> ZVON_USNI_PROTOCNICI # doctest:+ELLIPSIS
Category ZVON_USNI_PROTOCNICI (l,lj,r) at ...

>>> ZVON_USNI # doctest:+ELLIPSIS
Category ZVON_USNI (j,l,lj,r,v) at ...

>>> ZVON_NOSNI # doctest:+ELLIPSIS
Category ZVON_NOSNI (m,n,nj) at ...

>>> ZVONACNICI # doctest:+ELLIPSIS
Category ZVONACNICI (j,l,lj,m,n,nj,r,v) at ...

>>> ALPHABET - OTVORNICI.letters.union(ZATVORNICI.letters)
set([])

>>> TM_JEDRENICI # doctest:+ELLIPSIS 
Category TM_JEDRENICI (g,h,k) at ...

>>> sorted(TM_JEDRENICI.letters)
['g', 'h', 'k']

"""
# TODO: unfortenutelly this module has no good practial use, all logic went to suffix.py
#       check if module should be removed and/or isolated
from functools import partial
import codecs

ALPHABET = set(("a", "b", "c", "č", "ć", "d", "đ","dž", "e", "f", "g", "h", 
                "i", "j", "k", "l", "lj","m", "n","nj", "o", "p", "r", "s", 
                "š", "t", "u", "v", "z", "ž"))

class Glas(object):
    """
    >>> Glas("a") # doctest:+ELLIPSIS
    Glas(a) at ...
    >>> Glas("đ") # doctest:+ELLIPSIS
    Glas(đ) at ...
    >>> Glas("đ", "dž") # doctest:+ELLIPSIS
    Glas(đ/dž) at ...
    """
    def __init__(self, name, written=None):
        self.name, self.written =name, written
        self.categories = set()
        if not self.written:
            self.written=self.name

    #def __unicode__(self):
    #    return str(self)

    def __str__(self):
        if self.written!=self.name:
            return "Glas(%s/%s)" % (self.name, self.written)
        return "Glas(%s)" % (self.name,)

    def __repr__(self):
        return "%s at %X" % (str(self), id(self))

class Category(object):
    def __init__(self, name):
        self.name = name
        self.items = set()
        self.letters = set()

    def add(self, glas_or_letter):
        if isinstance(glas_or_letter, Glas):
            glas = self.items.add(glas_or_letter)
        else:
            glas = GLASOVI[glas_or_letter]
        self.items.add(glas)
        self.letters.add(glas.name)
        return glas

    def __str__(self):
        return "Category %s (%s)" % (self.name,",".join([str(g) for g in sorted(self.letters)]))

    def __repr__(self):
        return "%s at %X" % (str(self), id(self))


def normalize_letter(letter):
    assert letter.islower()
    letter = letter.replace("č", "ch")
    letter = letter.replace("ć", "cs")
    letter = letter.replace("š", "ch")
    letter = letter.replace("đ", "ch")
    letter = letter.replace("ž", "ch")
    return letter

def add_category(letter, category):
    """ makes crossref glas/category"""
    glas = category.add(letter)
    glas.categories.add(category)

GLASOVI = {}
GLASOVI_NORM = {}
for letter in ALPHABET:
    glas = Glas(letter)
    GLASOVI[letter] = glas
    #GLASOVI_NORM[normalize(letter)] = glas
GLASOVI["ie"]=Glas("ie", "ije")
GLASOVI_NORM["ie"]=Glas("ie", "ije")

OTVORNICI = Category("OTVORNICI")
map(partial(add_category, category=OTVORNICI), ("i", "e", "a", "o", "u", "ie"))

ZVON_USNI_PRIBLIZNICI = Category("ZVON_USNI_PRIBLIZNICI")
map(partial(add_category, category=ZVON_USNI_PRIBLIZNICI), ("v", "j"))

ZVON_USNI_PROTOCNICI = Category("ZVON_USNI_PROTOCNICI")
map(partial(add_category, category=ZVON_USNI_PROTOCNICI), ("r", "l", "lj"))

ZVON_USNI = Category("ZVON_USNI")
map(partial(add_category, category=ZVON_USNI), 
    ZVON_USNI_PRIBLIZNICI.letters.union(ZVON_USNI_PROTOCNICI.letters))

ZVON_NOSNI = Category("ZVON_NOSNI")
map(partial(add_category, category=ZVON_NOSNI), ("m", "n", "nj"))

ZVONACNICI = Category("ZVONACNICI")
map(partial(add_category, category=ZVONACNICI), 
    ZVON_USNI.letters.union(ZVON_NOSNI.letters))

ZAPORNICI = Category("ZAPORNICI")
map(partial(add_category, category=ZAPORNICI), ("b","d","g","p","t","k"))

TJESNACNICI = Category("TJESNACNICI")
map(partial(add_category, category=TJESNACNICI), ("s", "š", "z", "ž", "f", "h"))

SLIVENICI = Category("SLIVENICI")
map(partial(add_category, category=SLIVENICI), ("c", "č", "ć", "dž", "đ"))
# # c  = t + s
# # č  = t + š
# # ć  = t + š # meko t i meko š
# # dž = d + ž
# # đ  = d + ž # meko d i meko ž

SUMNICI = Category("SUMNICI") # konsonanti, suglasnici
map(partial(add_category, category=SUMNICI), 
    ZAPORNICI.letters.union(TJESNACNICI.letters.union(SLIVENICI.letters)))

SUMNICI = Category("SUMNICI") # konsonanti, suglasnici
map(partial(add_category, category=SUMNICI), 
    ZAPORNICI.letters.union(TJESNACNICI.letters.union(SLIVENICI.letters)))

ZATVORNICI = Category("ZATVORNICI")
map(partial(add_category, category=ZATVORNICI), 
    ZVONACNICI.letters.union(SUMNICI.letters))

# # tn - tvorbeni način 
TN_SUSTAVCI_SIBILANTI = Category("TN_SUSTAVCI_SIBILANTI") # piskavci
map(partial(add_category, category=TN_SUSTAVCI_SIBILANTI), ("c", "z", "s"))

TN_SUSTAVCI = Category("TN_SUSTAVCI") # piskavci
map(partial(add_category, category=TN_SUSTAVCI),
    TN_SUSTAVCI_SIBILANTI.letters.union(set(("č","ć","ž","š","đ","dž"))))

TN_PREKIDNICI = Category("TN_PREKIDNICI")
map(partial(add_category, category=TN_PREKIDNICI),
    ZAPORNICI.letters.union(SLIVENICI.letters))

# # tm - tvorbeno mjesto
TM_DVOUSNENICI = Category("TM_DVOUSNENICI")
map(partial(add_category, category=TM_DVOUSNENICI), ("p", "b", "m"))
TM_ZUBNO_USNENICI = Category("TM_ZUBNO_USNENICI")
map(partial(add_category, category=TM_ZUBNO_USNENICI), ("f", "v"))
TM_ZUBNICI = Category("TM_ZUBNICI") # dentali
map(partial(add_category, category=TM_ZUBNICI), ("t", "d", "n", "c", "z", "s"))
TM_DESNICI = Category("TM_DESNICI") # alveolari
map(partial(add_category, category=TM_DESNICI), ("r", "l"))
TM_PREDNEPCANICI = Category("TM_PREDNEPCANICI") # postalveolari/prepalatali
map(partial(add_category, category=TM_PREDNEPCANICI), ("č", "dž", "š", "ž"))
TM_NEPCANICI_PRAVI = Category("TM_NEPCANICI_PRAVI") # pravi palatali
map(partial(add_category, category=TM_NEPCANICI_PRAVI), ("ć", "đ", "j", "lj", "nj"))
TM_NEPCANICI = Category("TM_NEPCANICI") # tvrdonecanici/palatali
map(partial(add_category, category=TM_NEPCANICI),
    TM_PREDNEPCANICI.letters.union(TM_NEPCANICI_PRAVI.letters))
TM_JEDRENICI = Category("TM_JEDRENICI") # mekonepcanici, velari
map(partial(add_category, category=TM_JEDRENICI), ("k", "g", "h"))

# ---------- mapping ------------------
class Mappings(object):
    def __init__(self):
        self.names_by_code = {}
        self.map_by_code = {}
        self.map_by_letter = {}

    def add_mapping(self, code, name, letters_from, letters_to, letter_plus=None):
        """ accepts string or list/tuples
        >>> print MAPPINGS.pp_code("P")
        P - Palatalizacija
        g -> ž
        h -> š
        k -> č

        >>> print MAPPINGS.pp_code("-P")
        -P - Palatalizacija-reversed
        č -> k
        š -> h
        ž -> g

        >>> sorted(MAPPINGS.get_froms("P"))
        [u'g', u'h', u'k']

        >>> sorted(MAPPINGS.get_tos("P"))
        [u'\u010d', u'\u0161', u'\u017e']

        >>> print MAPPINGS.pp_code("-S")
        -S - Sibilarizacija-reversed
        c -> k
        s -> h
        z -> g
        """
        assert len(letters_from)==len(letters_to)
        code_rev = "-"+code
        assert code not in self.map_by_code
        assert code_rev not in self.map_by_code
        if letter_plus:
            name = "%s (+%s)" % (name, letter_plus)
        self.names_by_code[code]=name
        self.names_by_code[code_rev]=name+"-reversed"
        self.map_by_code[code] = {}
        self.map_by_code[code_rev] = {}
        for ch_from, ch_to in zip(letters_from, letters_to):
            if not isinstance(ch_from, unicode):
                ch_from = unicode(ch_from, "utf-8")
            if not isinstance(ch_to, unicode):
                ch_to = unicode(ch_to, "utf-8")
            # for ch in (ch_from, ch_to):
            #     # TODO: probably unicode will have problems, now is 2 chars long, should be unicode
            #     assert len(ch)==1 or ch in ("č", "ć", "ž", "š", "đ", "nj", "lj", "ie"), "ch '%s' has len %d" % (ch, len(ch))
            self.map_by_code[code][ch_from]=ch_to
            self.map_by_code[code_rev][ch_to]=ch_from
            self.map_by_letter.setdefault(ch_from, (ch_to  , code))
            self.map_by_letter.setdefault(ch_to  , (ch_from, code_rev))

    def get_froms(self, code):
        return self.map_by_code[code].keys()

    def get_tos(self, code):
        return self.map_by_code[code].values()
        
    def pp_code(self, code):
        ret = []
        ret.append("%s - %s" % (code, self.names_by_code[code]))
        for ch_from in sorted(self.map_by_code[code].keys()):
            ch_to = self.map_by_code[code][ch_from]
            ret.append("%s -> %s" % (codecs.encode(ch_from,"utf-8"), codecs.encode(ch_to,"utf-8")))
        return "\n".join(ret)

MAPPINGS = Mappings()
MAPPINGS.add_mapping("P", "Palatalizacija", ["k", "g", "h"], ["č", "ž", "š"])
MAPPINGS.add_mapping("S", "Sibilarizacija", ["k", "g", "h"], ["c", "z", "s"])
# TODO: nj and lj solve
MAPPINGS.add_mapping("J", "Jotacija",       ["cj", "dj", "gj", "hj", "kj", "lj", "nj", "sj", "tj", "zj"], 
                                            ["čj", "đj", "žj", "šj", "čj", "lj", "nj", "š", "ć", "ž"],
                                            "j")

MAPPINGS.add_mapping("I", "Jotacija-bpmv",  ["bj",   "pj",   "mj",   "vj"], 
                                            ["blj", "plj", "mlj", "vlj"],
                                            "j")
def _test():
    print "running doctests"
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()

