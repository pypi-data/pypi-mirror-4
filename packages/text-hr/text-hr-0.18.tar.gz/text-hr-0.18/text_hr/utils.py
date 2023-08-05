# coding=utf-8
# doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
"""
>>> from text_hr.base import _TYPE_LIST as TYPE_LIST # will load all word types
>>> from text_hr.base import _ATTR_LIST as ATTR_LIST
>>> sorted(TYPE_LIST.keys()) # doctest: +NORMALIZE_WHITESPACE
['ABBR', 'ADJ', 'ADV', 'CONJ', 'EXCL', 'N', 'NUM', 'PART', 'PREP', 
 'PRON.NEO.CH1', 'PRON.NEO.CH2', 'PRON.NEO.FIX', 'PRON.OSO', 'PRON.POK', 
 'PRON.POS', 'PRON.POV', 'PRON.PPO', 'PRON.UOD.IME', 
 'PRON.UOD.PRD', 'V']

>>> sorted(ATTR_LIST.keys()) # doctest: +NORMALIZE_WHITESPACE
['ADV_T', 'CONJ_T', 'DEC', 'EXCL_T', 'GEN', 'GRD', 'NTY', 'NUM', 'PER',
 'PER_3MFN', 'PER_MFN', 'PREP_T', 'PRON_T', 'TIM']

>>> sorted([k for k,v in TYPE_LIST.iteritems() if v.is_changeable]) # doctest: +NORMALIZE_WHITESPACE
['ADJ', 'N', 'NUM', 'PRON.NEO.CH1', 'PRON.NEO.CH2', 'PRON.OSO', 'PRON.POK', 'PRON.POS', 
 'PRON.POV', 'PRON.PPO', 'PRON.UOD.IME', 'PRON.UOD.PRD', 'V']

>>> sorted([k for k,v in TYPE_LIST.iteritems() if not v.is_changeable])
['ABBR', 'ADV', 'CONJ', 'EXCL', 'PART', 'PREP', 'PRON.NEO.FIX']


Testing all words:
>>> words = get_all_std_words()

>>> len(words)
2904

Testing all suffixes
--------------------
>>> suffixes = get_all_suffixes()

TODO: don't use suffixes directly - use word classes
#>>> len(suffixes)
#67

# >>> ", ".join(sorted([s.name for s in suffixes])) # doctest: +NORMALIZE_WHITESPACE
#     u'ADJ#P_N#, ADJ#P_N#-A#, ADJ#P_N+O#, ADJ#P_O#, 
#       N##A.M0.P-0, N##A.M0.P-0/P/G-i, N##A.M0.P-0/P/G-iju|a, 
#       N##A.M0.P-0/P/G-i|a, N##A.M0.P-ev, N##A.M0.P-ov, N##A.MOE.SN-e2, 
#       N##A.MOE.SN-e3, N##A.MOE.SN-oe, N##A.N-0, N##A.N-en, N##A.N-et, 
#       N##A.N.N, N##E.F.N-a, N##E.F.N-a/PG-%Aa, N##E.F.N-a/PG-%Ai, 
#       N##E.F.N-a/PG-%Au, N##E.F.N-a/SV-a, N##E.F.N-a/SV-e, N##EA.MOE, 
#       N##I.F.N-0, N##I.F.N-0/PG-iju, N##I.F.N-0/SI-u, 
#       PRON.NEO.CH2##sav, PRON.OSO#P/1#, PRON.OSO#P/2#vi, PRON.OSO#P/3M#, 
#       PRON.OSO#S/1#, PRON.OSO#S/2#ti, PRON.OSO#S/3F#, PRON.OSO#S/3M#, 
#       PRON.POK##ovaj, PRON.POK##ovakav, 
#       PRON.POS#P/1#na\u0161, PRON.POS#S/1#moj, PRON.POV##, 
#       PRON.UOD.IME##kakav, PRON.UOD.IME##tko, PRON.UOD.IME##\u0161to, PRON.UOD.PRD##koji, 
#       V#AOR#-h, V#AOR#-oh, V#AOR#biti, V#IMP#-ah, V#IMP#-ijah, V#IMP#-jah, 
#       V#IMV#-0, V#IMV#-i, V#IMV#biti/-i, V#PRE#-am, V#PRE#-em, V#PRE#-im, 
#       V#PRE#-jem, V#PRE#biti/NAG, V#PRE#biti/NEN, V#PRE#htjeti, 
#       V#PRE#morati/-jem, 
#       VA#ACT#-ao, VA#ACT#-o, VA#PAS#-en, VA#PAS#-jen, VA#PAS#-n, VA#PAS#-t'


"""

import os, sys, logging, codecs


_log_fname = ""
def init_logging(fname_log):
    global _log_fname
    if _log_fname:
        logging.warning("Log in %s, request to redirect to %s skipped" % (_log_fname, fname_log))
        return False
    _log_fname = os.path.join(os.path.dirname(__file__), fname_log)
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s %(levelname)-10s %(message)s',
                        filename=_log_fname,
                        filemode='w')
    logging.info("first init - log in %s" % _log_fname)
    return True

def iter_number_decl():
    import base
    for number in base.ATTR_NUMBER.values:
        for decl in base.ATTR_DECLINATION.values:
            yield number, decl

def iter_number_person():
    import base
    for number in base.ATTR_NUMBER.values:
        for person in base.ATTR_PERSON.values:
            yield number, person

def iter_number_gender():
    import base
    for number in base.ATTR_NUMBER.values:
        for gender in base.ATTR_GENDER.values:
            yield number, gender

class IterAttrs(object):
    def __init__(self, word_type_obj, suffix, suf_id, add_gender, iter_attrs, **attr_fix):
        """
        TODO: add_gender is not the best solution, callback could be better
        """
        self.iter_attrs = iter_attrs
        assert len(self.iter_attrs)==2
        self.word_type_obj = word_type_obj
        self.suffix, self.suf_id, self.add_gender = suffix, suf_id, add_gender
        for k,v in attr_fix.iteritems():
            setattr(self, k, v)

    def __iter__(self):
        """
        # NOTE: dropped - obsolete
        # >>> from nouns import NOUNS
        # >>> l = list(NOUNS.iter_suffix_cross_table())[0]
        # >>> l # doctest: +ELLIPSIS 
        # <....IterAttrs object at ...>
        # >>> l0 = list(l)
        # >>> len(l0)
        # 14
        # >>> l0[0]
        # ('S', 'N', ['$word_base0'])
        # >>> l0[-1]
        # ('P', 'I', ['%sima'])

        >>> from adjectives import ADJECTIVES
        >>> l = list(ADJECTIVES.iter_suffix_cross_table())[0]
        >>> l # doctest: +ELLIPSIS 
        <....IterAttrs object at ...>
        >>> l0 = list(l)
        >>> len(l0)
        14
        >>> l0[0]
        ('S', 'N', ['%a0'])
        >>> l0[-1]
        ('P', 'I', ['im', 'ima'])

        # >>> from verbs import VERBS
        # >>> l = list(VERBS.iter_suffix_cross_table())[0]
        # >>> l # doctest: +ELLIPSIS 
        # <....IterAttrs object at ...>
        # >>> l0 = list(l)
        # >>> len(l0)
        # 6
        # >>> l0[0]
        # ('S', '1', [u'em'])
        # >>> l0[-1]
        # ('P', '3', [u'u'])

        # >>> from verbs import VERBAL_ADJECTIVES
        # >>> l = list(VERBAL_ADJECTIVES.iter_suffix_cross_table())[0]
        # >>> l # doctest: +ELLIPSIS 
        # <....IterAttrs object at ...>
        # >>> l0 = list(l)
        # >>> len(l0)
        # 6
        # >>> l0[0]
        # ('S', 'M', [u'o'])
        # >>> l0[-1]
        # ('P', 'N', [u'la'])
        """
        import base
        for attr1 in self.iter_attrs[0].values:
            for attr2 in self.iter_attrs[1].values:
                if self.add_gender:
                    suf_values = self.suffix.suffixes["%s/%s/%s" % (attr1, attr2, self.gender)]
                else:
                    suf_values = self.suffix.suffixes["%s/%s" % (attr1, attr2)]
                yield attr1, attr2, suf_values

def get_all_suffixes():
    from text_hr.base import _TYPE_LIST as TYPE_LIST
    suffixes_all = set()
    for word_type_str, word_type in TYPE_LIST.iteritems():
        if word_type.is_changeable:
            suffixes_list = word_type.suffixes_dict.values()
            for suffixes_obj in suffixes_list: 
                suffixes_all.add(suffixes_obj)
    return suffixes_all

def get_all_std_words(wt_list=None):
    """
    TODO: explain
    htjeti               CH#V#                #PRE#NIJ#S/3#1                 'neće'
    htjeti               CH#V#                VA#ACT##P/3F#1                 'htjele'

    word_form            form descriptor
    'bi'                 'CH#biti#V#AOR#|P/3#2'
    explained:
        CH   - CH is changeable, FX is fixed
        biti - word_base
        V    - word_type_code
        AOR  - fixed attr values for this wt (separated with /)
        ''   - attr_extra value for this word form
        P/3  - changeable attr values for this wt (separated with /)
        2    - for same word form - several forms possible then counter distinguish them
    """
    from text_hr import morphs # will load all types
    from text_hr.base import _TYPE_LIST as TYPE_LIST

    words_all = []
    cnt_all = 0
    for word_type_str, word_type in TYPE_LIST.iteritems():
        if wt_list and word_type_str not in wt_list:
            continue
        if word_type.is_changeable:
            if word_type.std_words is not None: # happens to VA 
                for word_base, word_objs in word_type.std_words.iteritems():
                    if not isinstance(word_objs, (list, tuple)):
                        word_objs = [word_objs]
                    else:
                         # NOTE: currently the only case when this happens 
                         #       (two same word_bases for same word type) is in pronouns.osobne 
                         #       word_base S/2, P/3 "ona"
                         # , { "lexem" : "njo" , "word_base" : "ona"}
                         # , { "lexem" : "njim", "word_base" : "ona"}
                        pass
                    # TODO: in the case when there are more - put add descriptor in it - counter
                    for word_obj in word_objs:
                        word_base_key = "CH#%s#%s" % (word_type.code, "/".join([a for a in word_obj.attrs_fix]))

                        for suffixes_key, forms in word_obj.get_all_forms():
                            #>>> print VERBS.std_words["morati"].get_forms("PRE").pp_forms()
                            # if suffixes_key.startswith("VA#"):
                            #     assert word_type.code=="V"
                            # else:
                            assert suffixes_key.startswith(word_type.code+"#"), "%s & %s" % (suffixes_key, word_type.code)
                            # NOTE: this is not useful in tran import proc
                            # s1 = suffixes_key.split("#")
                            # s1[0]=""
                            # suffixes_key = "#".join(s1)

                            if isinstance(forms, basestring):
                                # V_ADV (glagolski pridjev prošli/sadašnji)
                                wform_key = "%s|%s#%d" % (suffixes_key, "", 1)
                                words_all.append((word_base, word_base_key, cnt_all, "", wform_key, forms))
                                cnt_all += 1
                            else:
                                suffixes_id = forms.suffixes.name
                                for form_key, wforms in forms.get_forms_ordered():
                                    assert wforms
                                    for i, wform in enumerate(wforms): 
                                        if wform:
                                            #descriptor = "CH#%s#%s|%s#%d" % (suffixes_key, form_key, i+1)
                                            wform_key = "%s|%s#%d" % (suffixes_key, form_key, i+1)
                                            words_all.append((word_base, word_base_key, cnt_all, suffixes_id, wform_key, wform ))
                                            cnt_all += 1
        else:
            for sub_type, word_set in word_type.std_words.wordset.iteritems():
                for word_base in word_set:
                    descriptor = "FX#%s#%s" % (word_type.code, sub_type)
                    words_all.append((word_base, descriptor, cnt_all, None, None, None))
                    cnt_all += 1

    return sorted(words_all)

def dump_all_std_words(fname=None, cp="utf8"):
    """
    if fname is not defined then output is dumped to 
    """
    words = get_all_std_words()
    if not fname:
        fname = os.path.join(os.path.dirname(__file__), "std_words.txt")
    f = codecs.open(fname, "w", cp)

    fmt = u"%-20s %-20s %-20s %-30s %s"
    line = fmt % ("Word base", "L.key", "Suffixes id", "W.form key", "W.form")
    f.write(line+"\n")
    for word_base, l_key, cnt, suffixes_id, wform_key, wform  in words:
        line = fmt % (word_base, l_key if l_key else "-", 
                      suffixes_id if suffixes_id else "-", 
                      wform_key if wform_key else "-", 
                      "%s" % (wform if wform else word_base))
        # NOTE: this is not needed, since it is done in write function
        # line = codecs.encode(line, cp) 
        f.write(line+"\n")
    f.close()
    msg = "Totaly %d word forms dumped to %s in codepage %s" % (len(words), fname, cp)
    print msg
    #logging.warning(msg)


# can be found in lujo.utils too
def to_unicode(s, cp="utf-8"):
    assert cp in ("utf8", "utf-8", "cp1250"), cp
    if isinstance(s, str):
        s = unicode(s, cp)
    assert isinstance(s, unicode),s
    return s

def from_unicode(s, cp="utf-8"):
    assert cp in ("utf8", "utf-8", "cp1250"), cp
    assert isinstance(s, unicode),s
    return codecs.encode(s, cp)

def iter_mine(*args):
    """
    for val in iter_mine():
        print val
    for val in iter_mine(2):
        print val
    for val in iter_mine(2,3):
        print val
    for val in iter_mine(2,3,2):
        print val
    #for val in iter_mine(2,3,2,1):
    #    print val
    """
    if not args:
        yield ()
        return
    # print "iter:", args
    for arg in args:
        assert isinstance(arg, int)
    if len(args)==1:
        for arg0 in range(args[0]):
            yield (arg0,)
    elif len(args)==2:
        for arg0 in range(args[0]):
            for arg1 in range(args[1]):
                yield (arg0, arg1)
    elif len(args)==3:
        for arg0 in range(args[0]):
            for arg1 in range(args[1]):
                for arg2 in range(args[2]):
                    yield (arg0, arg1, arg2)
    else:
        raise Exception("not implemented %d len" % (len(args),))

def get_exc_str():
    import traceback
    exc_info=sys.exc_info()
    if not exc_info[0]:
        return "No py exception"
    out="%s/%s/%s" % (str(exc_info[0]), str(traceback.extract_tb(exc_info[2])), str(exc_info[1]))
    #if bClear: sys.exc_clear()
    return out

# useful template
# doctest: +NORMALIZE_WHITESPACE
def test():
    # dump_all_std_words("r1.txt", cp="cp1250")
    # logging.basicConfig(level=logging.DEBUG, format='%(name)-10s %(levelname)-8s:%(message)s')
    # dump_all_std_words("r2.txt", cp="utf8")
    # dump_all_std_words("r3.txt", cp="utf16")
    print "%s: running doctests" % __name__
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    test()
