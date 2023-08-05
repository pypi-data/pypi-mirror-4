# coding=utf-8
import sys, os, codecs, logging, datetime

from morphs         import get_suff_registry, BadParamsInitError
from morphs         import _remove_vc_a, _apply_vc_a, AEIOU, split_by_last_AEIOU

from text_hr.utils  import get_exc_str, init_logging
from text_hr        import base

MAX_WORD_LENGTH = 30

class IWordTypeRecognizer(object):

    def __init__(self, silent=False):
        import sqlite3
        self.silent = silent
        self.conn = sqlite3.connect(":memory:")
        self.cur = self.conn.cursor()
        self.cur.execute("""create table words(
                                id integer not null primary key, 
                                value varchar(%d) not null, 
                                is_noun boolean,
                                freq integer unisigned not null,
                                for_process boolean
                                )""" % MAX_WORD_LENGTH)

        # RETURN_THIS: until this is solved in tran i use allow_dupl (bad example is zar -> z{
        # self.cur.execute("""create unique index words_unique on words(value, is_noun)""")
        self.cur.execute("""create index words_val_noun on words(value, is_noun)""")

        self.cur.execute("""create table wordobjs(
                                id integer not null primary key, 
                                id_other integer, 
                                word_type varchar(6) not null, 
                                word_base varchar(%d) not null, 
                                params_key varchar(40) not null, 
                                sri_key    varchar(40) not null, 
                                status_orig varchar(6) not null, 
                                is_noun_force boolean,
                                is_rejected boolean,
                                status_new  varchar(6) not null, 
                                weight float unisigned not null,
                                similar_word_ids varchar(100) not null, 
                                rejected_by integer)""" % MAX_WORD_LENGTH)

        self.cur.execute("""create unique index wordobjs_unique on wordobjs(word_type, word_base, params_key)""")
        # self.cur.execute("""create index wordobjs_ wordobjs(is_rejected, params_key)""")
        # self.word_objs_unique = {}
        self.word_objs_list = []
        self.word_forms = {}

    def add_word(self, id, word, freq, is_noun, for_process):
        self.cur.execute("insert into words(id, value, freq, is_noun, for_process) values(?,?,?,?,?)", 
                         (id, word, freq, is_noun, for_process))

    # NOTE: This is very similar to WordObj.key (i.e. _get_key)
    #def _get_key(self, word_type, word_base, params_key):
    #    return "%s(%s+%s)" % (word_base, word_type, params_key)

    # TODO: !!! this needs to go to table - faster and need to because other things
    #       create table wordobj(id, word_type, value_base, params_key, sri)
    def word_base_exists(self, word_type, word_base, params_key):
        # key = self._get_key(word_type, word_base, params_key)
        #word_obj = self.word_objs_unique.get(key, None)

        self.cur.execute("select id from wordobjs where word_type=? and word_base=? and params_key=?", 
                         (word_type, word_base, params_key,))
        row = self.cur.fetchone()
        if not row:
            return None
        return True

    # def get_word_obj(self, word_base):
    #     return self.word_objs.get(word_base, None)

    def save_new(self, word_type, word_base, params_key, word_obj, sri):
        # key = self._get_key(word_type, word_base, params_key)
        # assert key not in self.word_objs_unique.keys()

        # NOTE: word should not exist before
        # if self.word_base_exists(word_type, word_base, params_key):
        # #if key in self.word_objs_unique.keys():
        #     # TODO: make it strict, check in which cases this happen and process that
        #     #       currently these exceptions can happen:
        #     #       recognized by word %s but not found in word_obj.forms
        #     raise NotImplementedError("when this happens")
        #     return False

        # self.word_objs_unique[key]=word_obj
        # if word_obj:
        #     word_obj.__detect_key = key  # for debugging

        if word_obj is None:
            self.cur.execute(""" insert into wordobjs(
                                        word_type, word_base, params_key, sri_key,
                                        status_orig, is_noun_force, is_rejected, status_new,
                                        weight, similar_word_ids, rejected_by
                                 ) values (?,?,?,?,
                                           ?,?,?,?,
                                           ?,?,?)""", 
                             (
                             word_type, word_base, params_key, str(sri),
                             "", False, True, "R",
                             -1, "todo:", None
                             ))
            self.word_objs_list.append(None)
        else:
            self.cur.execute(""" insert into wordobjs(
                                        word_type, word_base, params_key, sri_key,
                                        status_orig, is_noun_force, is_rejected, status_new,
                                        weight, similar_word_ids, rejected_by
                                 ) values (?,?,?,?,
                                           ?,?,?,?,
                                           ?,?,?)""", 
                             (
                             word_type, word_base, params_key, str(word_obj.sri),
                             "", word_obj.status=="F", False, "T",
                             -1, "todo:", None
                             ))
            self.word_objs_list.append(word_obj)
            word_obj._id_saved = self.cur.lastrowid
            assert word_obj._id_saved
        return True

    def get_word_freq(self, word, is_noun_force=False):
        """ returns tuple freq, is_noun """
        self.cur.execute("select freq, is_noun, id from words where value=? order by is_noun %s" 
                            % ("desc" if is_noun_force else "asc"), (word,))
        row = self.cur.fetchone()
        if not row:
            return None
        return row

    # def get_word_id(self, word):
    #     self.cur.execute("select id from words where value=? order by is_noun desc", (word,))
    #     row = self.cur.fetchone()
    #     if not row:
    #         return None
    #     return row[0]


    def get_words_count(self):
        self.cur.execute("select count(*) from words")
        row = self.cur.fetchone()
        assert row, "no word in words"
        return row[0]

    def filter_starts_endswith(self, prefix, suff):
        return self._filter_starts_endswith(prefix, suff)

    def filter_endswith(self, suff):
        return self._filter_starts_endswith(None, suff)

    def _filter_starts_endswith(self, prefix, suff):
        # TODO: check implementing like this "... value like ?", ('%s%%%s' % (prefix, suff))
        if prefix:
            self.cur.execute("select value, is_noun from words where for_process=1 and value like '%s%%%s'" % (prefix, suff))
        else:
            self.cur.execute("select value, is_noun from words where for_process=1 and value like '%%%s'" % suff)
        result = [(row[0], row[1]) for row in self.cur.fetchall()]
        return result

    def reject(self, word_obj, other_obj):
        # NOTE: doesn't reject confirmed
        # assert key in self.word_objs_unique.keys()
        # word_obj = self.word_objs_unique[key]
        # TODO: assert word_obj, "%s already rejected" % key
        if (not word_obj.status=="F" 
            or not other_obj
            # TODO: not 100% that this won't cause duplicate same nouns
            or (     other_obj.word_type==word_obj.word_type
                 and other_obj.word_base==word_obj.word_base
                 and other_obj.status=="F")):
            if word_obj._id_saved:
                assert other_obj._id_saved
                self.cur.execute("""update wordobjs set is_rejected=1, rejected_by=? where id=?""", 
                                 (other_obj._id_saved, word_obj._id_saved, ))
            else:
                assert not other_obj
            word_obj._is_rejected = True
            # self.word_objs_unique[key]=None
            return True
        return False

    def dump_result(self, fname_or_file, cp="cp1250"):
        if isinstance(fname_or_file, basestring):
            fname = fname_or_file
            fout = file(fname, "w")
        else:
            fout = fname_or_file
            fname = getattr(fout, "name", "<noname-object>")
        logging.info("dump result to %s started" % fname)

        lines = []
        sum_freq = sum_exists = 0
        cnt_ok   = cnt_bad = 0

        for word_obj in self.word_objs_list:
            if not word_obj or word_obj._is_rejected:
                cnt_bad += 1
                continue
            cnt_ok += 1
            wf_with_freq = ["%6d/%s" % (item[0], wf.encode(cp, "replace")) 
                            for wf, item in word_obj.forms_stats.iteritems() if item[0]]
            occ_freq    = word_obj.get_forms_freq_sum()
            exists_freq = word_obj.get_forms_exists_freq_sum()
            sum_freq   += occ_freq
            sum_exists += exists_freq 
            assert len(wf_with_freq)==exists_freq

            stat_line = ",".join([w.strip() for w in sorted(wf_with_freq, reverse=True)])
            assert stat_line
            lines.append("%3d/%5d -> %-20s (%s) %s" % (exists_freq, occ_freq,
                                                word_obj.word_base.encode(cp, "replace"), 
                                                "confirmed" if word_obj.status=="F" else repr(word_obj.sri.key),
                                                stat_line))
        for line in sorted(lines, reverse=True):
            fout.write("%s\n" % (line,))

        msg = "from %d matched %d forms within %d word objects (bad/dupl/ignored %d) with exists freq %d (avg ~%.1f), and occ.freq %d (avg ~%.1f). output in %s." % (
              self.get_words_count(), len(self.word_forms), cnt_ok, cnt_bad, 
              sum_exists, sum_exists*1.0/(cnt_ok if cnt_ok else 1), 
              sum_freq  , sum_freq  *1.0/(cnt_ok if cnt_ok else 1), 
              fname)
        logging.info(msg)
        if not self.silent:
            print msg

    def detect(self, wt_filter=("N", "V", "ADJ"), level=2, from_tran=False, mode="load"):
        """
        level:
         - 0 - will search all, including base ""
         - 1 - will all but base index ""
         - (default) 2 - will skip suff with len=1 (e.g. a/o/e) these are very slow
         - 3 - will skip suff with len=2 (e.g. om, im)
         - 4 - will skip suff with len=3 (e.g. jom, jim)
        """
        assert level in [0,1,2,3,4], "invalid level"

        logging.info("detect started helper %s" % self)

        any = False
        if "ADJ" in wt_filter:
            any = True
        if "N" in wt_filter:
            any = True
        if "V" in wt_filter:
            any = True
        assert any, "bad word type filter: %s" % wt_filter

        # This takes long - 2 seconds?
        # 0, 1149, 2211, 6003

        started = datetime.datetime.now()
        last_ended = started

        if not self.silent:
            print "initializing wts forms ... (level=%d, mode=%s)" % (level, mode)

        if mode=="load":
            # FAST - load from file:
            suff_registry = get_suff_registry(init_all=True, load=True)
        elif mode=="store":
            # SLOW and STORE: 
            suff_registry = get_suff_registry(init_all=True, store=True)
        else:
            assert mode=="normal"
            # SLOW: 
            suff_registry = get_suff_registry(init_all=True)

        ended = datetime.datetime.now()
        if not self.silent:
            print "Duration %s" % (ended - started)

        logging.info("suffix registry is %s" % suff_registry)

        cnt_suff, len_suff = 0, len(suff_registry.suffix_dict)
        ind = 0

        cnt_new_obj = cnt_new_words = cnt_dupl=0
        cnt_word_obj_init_forms = 0

        # iterating suff_registry is sorted by suff_len
        for suff, sri_list in suff_registry: #.suffix_dict.iteritems():
            # REMOVE_THIS:
            # if suff not in ("lo", "o"):
            #     continue
            ind+=1
            # print repr((ind, suff, sri_list))
            cnt_suff +=1
            # TODO: the last param is not in all impl.
            # if cnt_suff>1000:
            #     print "TODO: remove me"
            #     break

            if not suff:
                continue
            if len(suff)<level: # shorter suffix longer search/more candidates - better results
                continue
            # NOTE: reducing sri_list - one sri entry per one sri.word_obj
            #       didn't get any performace boost
            sri_list_reduced = []
            _sri_word_objs = {}
            for sri in sri_list:
                # TODO: This will be a bit simplified when registry will hold only plain suffixes
                assert sri.suff_value==suff
                if sri.word_obj in _sri_word_objs:
                    continue
                sri_list_reduced.append(sri)
                _sri_word_objs[sri.word_obj]=True

            if "$" in suff: # if "$__lexem__$" in suff:
                raise NotImplementedError("never reached, and now ... prefix way not done yet")
                prefix = "naj"
            else:
                prefix = ""

            # detect duplicate values
            assert suff
            assert not [ch for ch in "%$_&-?" if ch in suff], suff

            if prefix:
                raise NotImplementedError("prefix way not done yet")
                word_list = list(self.filter_starts_endswith(prefix, suff))
            else:
                word_list = list(self.filter_endswith(suff))
                
            # http://guppy-pe.sourceforge.net/
            # http://stackoverflow.com/questions/110259/python-memory-profiler
            # if cnt_suff%500==0:
            #     from guppy import hpy
            #     h = hpy()
            #     print h.heap()
            for i_word, item in enumerate(word_list):
                word, is_noun = item
                # try to find other words
                wforms_found = []
                if word.startswith("naj"):
                    word_prepared = word[len("naj"):]
                else:
                    word_prepared = word

                if not word_prepared:
                    continue

                for i_sri, sri in enumerate(sri_list_reduced):
                    if not self.silent:
                        print "wn=%12s, suff=%15s %4d/%4d, wb=%4d/%4d, sri=%4d/%4d %s\r" % (
                                                        "%d/%d/%d/%d/%d" %(
                                                        cnt_dupl, cnt_new_obj,
                                                        cnt_word_obj_init_forms,
                                                        cnt_new_words, 
                                                        len(self.word_objs_list), 
                                                        ),
                                                        repr(suff), cnt_suff, len_suff, 
                                                        i_word, len(word_list),
                                                        i_sri+1, len(sri_list), repr(sri.word_obj.word_base), 
                                                        ),
                    min_suff_length = 1 if sri.word_obj.word_base=="" else 2
                    if len(suff)<min_suff_length:
                        continue

                    word_type = sri.word_type.code
                    if word_type not in wt_filter:
                       continue 

                    # NOTE: for adjectives this is not the case
                    # TODO: check nouns and verbs - get word_base from w and sri, remove vc
                    #       how to deal with vc-s? - do remove ... detect on form
                    #       just for reference - this cant be used: add_vts(apply_vc_a, apply_vc_all, vc_list)
                    word_obj_confirmed = None
                    if sri.word_obj.status=="F":
                        assert not sri.word_obj.is_suffix
                        word_obj_confirmed = sri.word_obj
                        word_base = word_obj_confirmed.word_base
                    elif word_type=="V":
                        assert sri.word_obj.is_suffix
                        word_base = word_prepared[:-len(suff)]
                        # NOTE: full words possible - e.g. pasti 
                        #       thus check is not needed: 
                        #       if len(word_base)<1: continue
                        word_base = word_base+sri.word_obj.word_base
                    else:
                        #if not sri.word_obj.is_suffix:
                        #    import pdb;pdb.set_trace() 
                        assert sri.word_obj.is_suffix
                        word_base = word_prepared[:-len(suff)]
                        # for N and ADJ min length is 3 
                        if word_type=="ADJ":
                            if len(word_base)<3:
                                continue
                        elif word_type=="N":
                            if len(word_base)<2:
                                continue
                        # default sri.wts.base_ends_aeiou is None
                        if sri.wts.base_ends_aeiou in (True, False):
                            base_last_char_when_AEIOU = split_by_last_AEIOU(word_base)[1]
                            if sri.wts.base_ends_aeiou==True:
                                if base_last_char_when_AEIOU=="":
                                    continue
                            else:
                                assert sri.wts.base_ends_aeiou==False
                                if base_last_char_when_AEIOU!="":
                                    continue
                        word_base = word_base+sri.word_obj.word_base

                    if len(word_base)<3:
                        continue

                    # TODO: same word in diff scenarios
                    params_key=sri.word_obj.params_key
                    params_init=sri.word_obj.params_init
                    word_obj_found = self.word_base_exists(word_type=word_type, word_base=word_base, 
                                                           params_key=params_key)
                    if word_obj_found:
                        # # what is this??
                        # if sri.suff_value=="njem":
                        #     out = "Found already processed - skipped: this: %s, %s,%s, found: %s, %s" % (
                        #             sri, sri.suff_value, word_list, word_obj_found, word_obj_found.sri)
                        #     logging.info(out)
                        cnt_dupl+=1
                        continue

                    if word_obj_confirmed:
                        word_obj = word_obj_confirmed
                        word_class = word_obj.__class__
                    else:
                        word_class = sri.word_obj.__class__

                        try:
                            cnt_new_obj+=1
                            word_obj = word_class(word_base=word_base, 
                                                 sri=sri,
                                                 **params_init)
                        except BadParamsInitError, e:
                            logging.info("%s(%s, %s, %s) params_init is invalid. Ignored (%s)" % (
                                          word_class.__name__,
                                          repr(word_base), sri, 
                                          repr(params_key), repr(e)))
                            self.save_new(word_type, word_base, params_key, None, sri)
                            continue
                        except Exception, e:
                            logging.exception("%s(%s, %s, %s) returned:\n   %s" % (
                                            word_class.__name__,
                                            word_base, sri, 
                                            repr(params_key), get_exc_str()))
                            self.save_new(word_type, word_base, params_key, None, sri)
                            continue

                    # NOTE: params_key can change
                    params_key=word_obj.params_key
                    word_obj_found = self.word_base_exists(word_type=word_type, word_base=word_base, 
                                                           params_key=params_key)
                    if word_obj_found:
                        cnt_dupl+=1
                        continue

                    # N-a-moeD/+A/mG/$E/$S_M_-ova-0
                    if word_obj.word_base_changed:
                        word_base = word_obj.word_base
                        if self.word_base_exists(word_type=word_type, word_base=word_base, 
                                                 params_key=params_key):
                            cnt_dupl+=1
                            continue
                    try:
                        # here is another try/catch - because init_forms can produce such problems
                        # e.g. base form not found
                        cnt_word_obj_init_forms+=1
                        if not word in word_obj.forms_stats.keys():
                            #if "brojati"==word_base: # brojeći
                            logging.warning("%s(%s/%s, %s, %s) recognized by word %s but not found in word_obj.forms" % (
                                            word_class.__name__,
                                            word_base, word_obj.word_lexem, 
                                            sri, repr(params_key), word))
                            self.reject(word_obj, None)
                            # self.save_new(word_type, word_base, params_key, None, sri)
                            continue
                    except Exception, e:
                        # TODO: make DRY 
                        if isinstance(e, BadParamsInitError):
                            logging.info("%s(%s, %s, %s) params_init (2) is invalid. Ignored (%s)" % (
                                          word_class.__name__,
                                          repr(word_base), sri, 
                                          repr(params_key), repr(e)))
                        else:
                            logging.exception("%s(%s, %s, %s) params_init (2) fatal error. continuing (%s)" % (
                                          word_class.__name__,
                                          repr(word_base), sri, 
                                          repr(params_key), repr(e)))
                            
                        self.save_new(word_type, word_base, params_key, None, sri)

                        continue

                    # print "%s(%s, %s) - %d / %d - %s" % (word_class.__name__,word_base, repr(params_key), len(word_obj.forms_flat), len(word_obj.forms_stats), sri)
                    cnt_found = 0
                    word_obj.cnt_wf_noun=0
                    for wf in word_obj.forms_stats.keys():
                        if "$" in wf:
                            # TODO: "$__lexem__$" in naj$__lexem__$uljastija
                            raise NotImplementedError("this should have been reached, but didn't and now ... how that?")
                        result = self.get_word_freq(wf)
                        if result:
                            word_freq, is_wf_noun, word_id = result
                            assert word_obj.forms_stats[wf][0]==0
                            word_obj.set_form_freq(wf, word_freq, word_id)
                            cnt_found += 1
                            if is_wf_noun:
                                word_obj.cnt_wf_noun+=1
                    if not cnt_found:
                        # when true this could happen, but when false, then it is strange
                        if params_init.get("apply_vc_a", None)==False:
                            logging.warning("%s(%s, %s, %s) word_base %s found and then not found" % (
                                            word_class.__name__,
                                            word_base, sri, repr(params_key), word_base))
                        self.save_new(word_type, word_base, params_key, None, sri)
                    else:
                        # This one is good
                        if (not word_obj.status=="F" and 
                            word_obj.word_type.code=="N" and word_obj.cnt_wf_noun>0):
                            word_obj.status="F"
                        if self.save_new(word_type, word_base, word_obj.params_key, word_obj, sri):
                            cnt_new_words+=1
                        else:
                            # "TODO: when this happens"
                            pass
                            # import pdb;pdb.set_trace() 
            # end of suff (sri_list x words)?
            now = datetime.datetime.now()
            duration = now - last_ended
            last_ended = now
            if word_list:
                logging.info("duration: %-17s, count: %4d x %4d (sri,%4d) =%6d, new_obj=%4d, new_words=%4d, filter %s/%s" % (
                             duration, len(word_list), len(sri_list_reduced), len(sri_list), 
                             len(word_list) * len(sri_list_reduced),
                             cnt_new_obj, cnt_new_words, prefix, suff,))


        if not self.silent:
            print ""
        logging.info("detect main loop ended")
        ended = datetime.datetime.now()
        if not self.silent:
            print "Duration %s" % (ended - started)

        if not self.silent and not from_tran:
            fname_out = "testing_w_br-bef-reduction.out" if level==2 else ("testing_w_br-bef-reduction-%d.out" % level)
            self.dump_result(fname_out)
        logging.info("detect reduction started")
        self._detect_reduction()
        logging.info("detect reduction ended")
        ended = datetime.datetime.now()
        if not self.silent:
            print "Duration %s" % (ended - started)


    def _detect_reduction(self):
        # TODO: this doesn't belong here but in post-process od detect
        self.word_forms = {}

        # fill word_forms
        # for word_base, word_obj_list in self.iter_new_word_obj_lists():
        # for key, word_obj in self.word_objs_unique.iteritems():
        for word_obj in self.word_objs_list:
            if not word_obj or word_obj._is_rejected: # because word_base is not found
                continue
            for wf in word_obj.get_forms_exists_set():
                if wf not in self.word_forms:
                    self.word_forms[wf] = []
                self.word_forms[wf].append(word_obj)

        # TODO: example. brbljav is recognized by has_neo=T/F, has_com=T/F
        #       which to use? if any found in neo, then neo=T
        #                     if any found in com, com=T
        #       but in other cases, you can't be sure if to use F
        #       in that case we should use None (don't know yet)
        # NOTE: choose the best:
        #   20/  106 -> brutalan             (SRI(u'nijih', u'ADJ-oo_ji_-_AN-COM/P/G/M-1')) 35/brutalno,11/brutalna,10/brutalnim,7/brutalnu,7/brutalni,6/brutalan,5/brutalnog,5/brutalne,4/brutalnom,3/brutalnoj,2/najbrutalniji,2/brutalnije,2/brutalnih,1/najbrutalnijoj,1/najbrutalnijim,1/najbrutalnijih,1/najbrutalnije,1/najbrutalnija,1/brutalnome,1/brutalniji
        #   19/  100 -> brutalni             (SRI(u'jim', u'ADJ-+a/-n/+c/ji_-_-COM/S/I/M-1')) 35/brutalno,11/brutalna,10/brutalnim,7/brutalnu,7/brutalni,5/brutalnog,5/brutalne,4/brutalnom,3/brutalnoj,2/najbrutalniji,2/brutalnije,2/brutalnih,1/najbrutalnijoj,1/najbrutalnijim,1/najbrutalnijih,1/najbrutalnije,1/najbrutalnija,1/brutalnome,1/brutalniji
        #   19/  100 -> brutaln              (SRI(u'ijoj', u'ADJ--a/+n/+c/iji_-_-COM/S/D/F-1')) 35/brutalno,11/brutalna,10/brutalnim,7/brutalnu,7/brutalni,5/brutalnog,5/brutalne,4/brutalnom,3/brutalnoj,2/najbrutalniji,2/brutalnije,2/brutalnih,1/najbrutalnijoj,1/najbrutalnijim,1/najbrutalnijih,1/najbrutalnije,1/najbrutalnija,1/brutalnome,1/brutalniji

        compared = {}

        # for this_key, word_obj in self.word_objs_unique.iteritems():
        for word_obj in self.word_objs_list:
            if not word_obj or word_obj._is_rejected: # because word_base is not found
                continue
            this_exists_set = word_obj.get_forms_exists_set()
            this_set = word_obj.get_forms_set()
            this_key = word_obj.key
            rejected_this = False
            for wf in this_exists_set:
                if rejected_this:
                    break
                for other_obj in self.word_forms[wf]:
                    # other_key = self._get_key(other_obj.word_type.code, other_obj.word_base, other_obj.params_key)
                    other_key = other_obj.key

                    #other_obj_exists = self.word_objs_unique[other_key]
                    #if not other_obj_exists:
                    if other_obj._is_rejected:
                        continue

                    if other_key==this_key:
                    #if other_obj.word_base==word_obj.word_base:
                        continue
                    comp_key1 = "%s||%s" % (this_key, other_key)
                    comp_key2 = "%s||%s" % (other_key, this_key)
                    comp_key_min = comp_key1 if comp_key1<comp_key2 else comp_key2

                    if comp_key_min in compared:
                        continue
                    compared[comp_key_min]=True

                    other_exists_set = other_obj.get_forms_exists_set()

                    has_this  = this_exists_set - other_exists_set
                    has_other = other_exists_set - this_exists_set
                    has_both  = this_exists_set & other_exists_set

                    assert wf in has_both

                    # get simmilar
                    other_set = other_obj.get_forms_set()
                    has_forms_both = this_set & other_set

                    # TODO: is it better to save complete word or _id_saved?
                    if False: # TODO: disabled for performance issues?
                        assert other_obj.key not in word_obj.similar_words
                        assert word_obj.key  not in other_obj.similar_words

                        # register similar words
                        # (at least one has_both and 5 same forms) or (3 same forms that exists, i.e. freq>0)
                        if len(has_forms_both)>=5 or len(has_both)>=3:
                            # TODO: this is not throughly tested
                            word_obj.similar_words[other_obj.key]=(other_obj, len(has_forms_both), len(has_both))
                            other_obj.similar_words[word_obj.key]=(word_obj, len(has_forms_both), len(has_both))

                    # if  (    unicode("brbljanje", "utf-8") in (word_obj.word_base, other_obj.word_base)):
                    #      #and unicode("brbljavc", "utf-8")  in (word_obj.word_base, other_obj.word_base)):
                    #      out =      "1 %s %s %s" % (word_obj, word_obj.sri, word_obj.params_key)
                    #      out +="\n"+"2 %s %s %s" % (other_obj, other_obj.sri, other_obj.params_key)
                    if (    "N" in (word_obj.word_type.code, other_obj.word_type.code) 
                        and "V" in (word_obj.word_type.code, other_obj.word_type.code)):
                        noun_obj = word_obj if word_obj.word_type.code=="N" else other_obj
                        if noun_obj.word_base.endswith("lo"):
                            # will leave both - both are good
                            has_this ="N.LO=V exception"
                            has_other="N.LO=V exception"
                    elif (  "ADJ" in (word_obj.word_type.code, other_obj.word_type.code) 
                        and "V"   in (word_obj.word_type.code, other_obj.word_type.code)):
                        adjective_obj, verb_obj = (word_obj, other_obj) if word_obj.word_type.code=="ADJ" else (other_obj, word_obj)
                        if (adjective_obj.word_base.endswith("at") 
                            and not (    len(has_both)==1 
                                     and tuple(has_both)[0]==verb_obj.word_base)):
                            # will leave both - both are good
                            has_this ="ADJ.AT=V exception"
                            has_other="ADJ.AT=V exception"

                    if has_this and has_other:
                        # will leave both - both are good
                        logging.info("%s is like %s - saving both (this: %s, oth: %s)" % (other_obj, word_obj, has_this, has_other))
                    elif has_this:
                        logging.info("%s is like %s but worse, so rejecting it (this: %s)" % (other_obj, word_obj, has_this))
                        is_rejected = self.reject(other_obj, word_obj)
                    elif has_other:
                        logging.info("%s is like %s but worse, so rejecting it (oth: %s)" % (other_obj, word_obj, has_other))
                        if self.reject(word_obj, other_obj):
                            rejected_this = True
                            break
                    else:
                        if word_obj.is_better_than(other_obj):
                            logging.info("%s is like %s but worse, so rejecting it (both: %s)" % (other_obj, word_obj, has_both))
                            is_rejected = self.reject(other_obj, word_obj)
                        else:
                            logging.info("%s is like %s but worse, so rejecting it (both: %s)" % (other_obj, word_obj, has_both))
                            if self.reject(word_obj, other_obj):
                                rejected_this = True
                                break

            # TODO: what about those with low freq, low word_forms ... - if suffix is unique and is long enough then save, else not

        # for word_base, word_obj_list in self.iter_new_word_obj_lists():
        #     word_obj_best, sum_freq_best = None, 0
        #     for word_obj in word_obj_list:
        #         if word_obj_best is None or word_obj.is_better_than(word_obj_best):
        #             word_obj_best = word_obj
        #     if not word_obj_best:
        #         self.save_best(word_base, None) # reduce
        #         continue
        #     #assert sum_freq_best>=FREQ_TRESHOLD
        #     self.save_best(word_base, word_obj_best) # choose

        #     assert word_obj_best
        #     for wf in word_obj_best.get_forms_exists_set():
        #         if wf not in self.word_forms:
        #             self.word_forms[wf] = []
        #         self.word_forms[wf].append(word_obj_best)

            # if wb_test[-1] in AEIOU:
            #     wb_test = wb_test[:-1]
            #     # for suff in [""] + [ch for ch in AEIOU]:
            #     suff = ""
            #     word_obj_other = self.get_word_obj(wb_test+suff)
            #     if word_obj_other:
            #         if word_obj.is_better_than(word_obj_other):
            #             logging.info("%s is like %s but worse, so rejecting it" % (word_obj_other, word_obj))
            #             self.save_best(word_obj_other.word_base, None)
            #         else:
            #             logging.info("%s is like %s but worse, so rejecting it" % (word_obj, word_obj_other))
            #             self.save_best(word_obj.word_base, None)
            #             word_obj = word_obj_other  # switch - use other - and check it too
            # wb_test_applied = _remove_vc_a(wb_test)
            # if wb_test!=wb_test_applied:
            #     word_obj_other = self.get_word_obj(wb_test_applied)
            #     if word_obj_other:
            #         if word_obj.is_better_than(word_obj_other):
            #             logging.info("%s is like %s but worse, so rejecting it" % (word_obj_other, word_obj))
            #             self.save_best(word_obj_other.word_base, None)
            #         else:
            #             logging.info("%s is like %s but worse, so rejecting it" % (word_obj, word_obj_other))
            #             self.save_best(word_obj.word_base, None)


class WordTypeRecognizerExample(IWordTypeRecognizer):

    def __init__(self, iter_obj, silent=False):
        super(WordTypeRecognizerExample, self).__init__(silent)

        for i, line in enumerate(iter_obj):
            line = line.strip()
            if not line:
                continue
            fields = line.split()
            assert len(fields)==2, fields
            word, freq = fields
            if word.startswith("-"):
                word = word[1:]
                for_process = False
            else:
                for_process = True
            is_noun = (word[0].isupper() and word[0].isalpha())
            self.add_word(i+1, word.lower(), freq, is_noun, for_process)
        self.conn.commit()

def test(from_tran=False, do_all=True, level=2, mode="load"):
    import doctest
    # print "%s: running doctests" % __name__
    # doctest.testmod()
    if not do_all:
        base.run_doctests( ("test_detect.txt", ))
        return

    init_logging(fname_log = "detect.log")

    if from_tran:
        """ Usage:
        > tran shell
        >>> from text_hr import detect
        >>> detect.test(from_tran=True, level=3)
        """
        # TODO: this won't be running ;)
        from lujo.django.apps.tran.models import WordTypeRecognizer
        filter_ch, filter_for_process, delete_last_detected="bris", None, False
        wdh = WordTypeRecognizer(filter_ch=filter_ch, 
                                 filter_for_process=filter_for_process, 
                                 delete_last_detected=delete_last_detected)
    else:
        iter_obj = codecs.open("testing_w_br.txt", "r", "utf-8")
        wdh = WordTypeRecognizerExample(iter_obj)

    wdh.detect(level=level, from_tran=from_tran, mode=mode)

    if from_tran:
        print "calling wdh.save_result()"
        started = datetime.datetime.now()

        wdh.save_result()

        ended   = datetime.datetime.now()
        print "Duration %s" % (ended - started)
    else:
        fname_out = "testing_w_br.out" if level==2 else ("testing_w_br-lev-%d.out" % level)
        wdh.dump_result(fname_out)

if __name__=="__main__":
    do_all = (len(sys.argv)>=2 and sys.argv[1].lower()=="all")
    mode   = "store" if (len(sys.argv)>=3 and sys.argv[2].lower()=="store") else "load"
    level  = 2 if not (len(sys.argv)>=3 and sys.argv[2].isdigit()) else int(sys.argv[2])
    test(do_all=do_all, level=level, mode=mode)

