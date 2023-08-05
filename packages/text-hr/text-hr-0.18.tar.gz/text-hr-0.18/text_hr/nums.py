# coding=utf-8
#...    print "%-40s " % val, # doctest: +NORMALIZE_WHITESPACE
"""
#>>> print SUFF_ADJ["P_N"].pp_forms_gender("crven") # doctest: +NORMALIZE_WHITESPACE
"""
# TODO: nisam numbers
import base
if not base.is_word_type_registred("NUM"):
    NUMBERS     = base.ChangeableWordType("NUM", "Brojevi", attrs_fix=[base.ATTR_NUM_TYPE], 
                           attrs_ch=[base.ATTR_PERSON, base.ATTR_DECLINATION, base.ATTR_GENDER]) # gender?? maybe person_mfn
    WORD_TYPE = NUMBERS
else:
    WORD_TYPE = base.get_word_type("NUM")
# SUFFIXES = {}
WORDS = {}

# SUFFIXES["NUM"]={}
WORDS["NUM"]={}

# TODO: nisam ih, a nije komplicirano
# from morphs import WordSuffixes
# import wtypes
# SUFF_NUM = {}
# def test():
#     print "%s: running doctests" % __name__
#     import doctest
#     doctest.testmod()
#     base.run_doctests(( "test_nums.txt", ))
# 
# if __name__ == "__main__":
#     test()


