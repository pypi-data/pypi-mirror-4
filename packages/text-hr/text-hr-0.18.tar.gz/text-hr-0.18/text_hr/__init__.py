# coding=utf-8
from   base   import _TYPE_LIST as TYPE_LIST
from   base   import _ATTR_LIST as ATTR_LIST

from fix_words  import ADVERBS, PREPOSITIONS, CONJUCTIONS, EXCLAMATIONS, PARTICLES    
# import fix_words
import pronouns
# hr specific
# from pronouns   import (PRONOUNS_NEO_CH1, PRONOUNS_NEO_CH2, PRONOUNS_NEO_FIX, 
#                         PRONOUNS_OSO, PRONOUNS_POK, PRONOUNS_POS, PRONOUNS_POV, 
#                         PRONOUNS_PPO, PRONOUNS_UOD_IME, PRONOUNS_UOD_PRD)
import detect
from   verbs      import Verb, VERBS
from   adjectives import Adjective, ADJECTIVES
from   nouns      import Noun, NOUNS
# # in py-2.6 - numbers is module
import nums as _nums_todo
from morphs import BadParamsInitError

from   utils import get_all_suffixes, get_all_std_words, dump_all_std_words

__all__ = [ "Noun", "Adjective", "Verb", 
            "BadParamsInitError",
            "fix_words", "adjectives", "nouns", 
            "nums",      "pronouns",   "verbs", "detect" ]

if __name__ == "__main__":
    pass
