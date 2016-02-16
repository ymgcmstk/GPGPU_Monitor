#!/usr/bin/env python
# -*- coding:utf-8 -*-

import copy
import cPickle
import httplib
import json
import os
import pickle
import shutil
import sys
import time
import threading
import urllib
import urllib2

try:
    import ymgc_toolbox
    gmail         = ymgc_toolbox.gmail
    cp2www        = ymgc_toolbox.cp2www
    get_example = ymgc_toolbox.get_example
except:
    def gmail(*input1, **input2):
        print 'gmail() cannot be loaded.'
        return
    def cp2www(*input1, **input2):
        print 'cp2www() cannot be loaded.'
        return
    def get_example(*input1, **input2):
        print 'get_test_file() cannot be loaded.'
        return

def set_debugger(send_email=False, error_func=None):
    if hasattr(sys.excepthook, '__name__') and sys.excepthook.__name__ == 'apport_excepthook':
        from IPython.core import ultratb
        class MyTB(ultratb.FormattedTB):
            def __init__(self, mode='Plain', color_scheme='Linux', call_pdb=False,
                         ostream=None,
                         tb_offset=0, long_header=False, include_vars=False,
                         check_cache=None, send_email=False, error_func=None):
                self.send_email   = send_email
                self.color_scheme = color_scheme
                self.error_func   = error_func
                ultratb.FormattedTB.__init__(self, mode=mode, color_scheme=color_scheme,
                                             call_pdb=call_pdb, ostream=ostream,
                                             tb_offset=tb_offset, long_header=long_header,
                                             include_vars=include_vars, check_cache=check_cache)
            def __call__(self, etype=None, evalue=None, etb=None):
                if self.send_email and not etype.__name__ == 'KeyboardInterrupt':
                    try:
                        title = 'Debugger has been called in "%s" on %s.' % (sys.argv[0], os.uname()[1])
                        self.set_colors('NoColor')
                        body  = self.text(etype, evalue, etb)
                        self.set_colors(self.color_scheme)
                        gmail(title, body)
                    except:
                        pass
                ultratb.FormattedTB.__call__(self, etype=etype, evalue=evalue, etb=etb)
                if self.error_func is not None:
                    try:
                        self.error_func()
                    except:
                        pass
        sys.excepthook = MyTB(call_pdb=True, send_email=send_email, error_func=error_func)
        print 'MyTB has been set to except hook.'

def set_debugger_org():
    if not sys.excepthook == sys.__excepthook__:
        from IPython.core import ultratb
        sys.excepthook = ultratb.FormattedTB(call_pdb=True)

class TimeReporter:
    def __init__(self, max_count, interval=1, moving_average=False):
        self.time           = time.time
        self.start_time     = time.time()
        self.max_count      = max_count
        self.cur_count      = 0
        self.prev_time      = time.time()
        self.interval       = interval
        self.moving_average = moving_average
    def report(self, cur_count=None, max_count=None, overwrite=True, prefix=None, postfix=None, interval=None):
        if cur_count is not None:
            self.cur_count = cur_count
        else:
            self.cur_count += 1
        if max_count is None:
            max_count = self.max_count
        cur_time = self.time()
        elapsed  = cur_time - self.start_time
        if self.cur_count <= 0:
            ave_time = float('inf')
        elif self.moving_average and self.cur_count == 1:
            ave_time = float('inf')
            self.ma_prev_time = cur_time
        elif self.moving_average and self.cur_count == 2:
            self.ma_time      = cur_time - self.ma_prev_time
            ave_time          = self.ma_time
            self.ma_prev_time = cur_time
        elif self.moving_average:
            self.ma_time      = self.ma_time * 0.95 + (cur_time - self.ma_prev_time) * 0.05
            ave_time          = self.ma_time
            self.ma_prev_time = cur_time
        else:
            ave_time = elapsed / self.cur_count
        ETA = (max_count - self.cur_count) * ave_time
        print_str = 'count : %d / %d, elapsed time : %f, ETA : %f' % (self.cur_count, self.max_count, elapsed, ETA)
        if prefix is not None:
            print_str = str(prefix) + ' ' + print_str
        if postfix is not None:
            print_str += ' ' + str(postfix)
        this_interval = self.interval
        if interval is not None:
            this_interval = interval
        if cur_time - self.prev_time < this_interval:
            return
        if overwrite and self.cur_count != self.max_count:
            printr(print_str)
            self.prev_time = cur_time
        else:
            print print_str
            self.prev_time = cur_time

def textread(path):
    f = open(path)
    lines = f.readlines()
    f.close()
    for i in range(len(lines)):
        lines[i] = lines[i].replace('\n', '')
    return lines

def textdump(path, lines, need_asking=False):
    if os.path.exists(path) and need_asking:
        if 'n' == choosebyinput(['Y', 'n'], path + ' exists. Would you replace? [Y/n]'):
            return False
    f = open(path, 'w')
    for i in lines:
        f.write(i + '\n')
    f.close()

def pickleload(path):
    # if not os.path.exists(path):
    #     print path, 'does not exist.'
    #     return False
    f = open(path)
    this_ans = pickle.load(f)
    f.close()
    return this_ans

def pickledump(path, this_dic):
    f = open(path, 'w')
    this_ans = pickle.dump(this_dic, f)
    f.close()

def cPickleload(path):
    # if not os.path.exists(path):
    #     print path, 'does not exist.'
    #     return False
    f = open(path, 'rb')
    this_ans = cPickle.load(f)
    f.close()
    return this_ans

def cPickledump(path, this_dic):
    f = open(path, 'wb')
    this_ans = cPickle.dump(this_dic, f, -1)
    f.close()

def jsonload(path):
    # if not os.path.exists(path):
    #     print path, 'does not exist.'
    #     return False
    f = open(path)
    this_ans = json.load(f)
    f.close()
    return this_ans

def jsondump(path, this_dic):
    f = open(path, 'w')
    this_ans = json.dump(this_dic, f)
    f.close()

def choosebyinput(cand, message=False):
    if not type(cand) == list and not type(cand) == int:
        print 'The type of cand_list has to be \'list\' or \'int\' .'
        return
    if type(cand) == int:
        cand_list = range(cand)
    if type(cand) == list:
        cand_list = cand
    int_cand_list = []
    for i in cand_list:
        if type(i) == int:
            int_cand_list.append(str(i))
    if message == False:
        message = 'choose by input : ['
        for i in int_cand_list:
            message += i + ' / '
        for i in cand_list:
            if not str(i) in int_cand_list:
                message += i + ' / '
        message = message[:-3] + ']'
    while True:
        your_ans = raw_input(message)
        if your_ans in int_cand_list:
            return int(your_ans)
            break
        if your_ans in cand_list:
            return your_ans
            break

def mv_files(name1, name2, targ_dir=None):
    if targ_dir is None:
        files = os.listdir('.')
    else :
        files = [os.path.join(targ_dir, fname) for fname in os.listdir(targ_dir)]
    for this_file in files:
        if name1 in this_file:
            flg = True
            if os.path.exists(this_file.replace(name1, name2)):
                your_ans = choosebyinput(['Y', 'n'], message=this_file.replace(name1, name2) + ' exists. Would you replace? [Y/n]')
                if your_ans == 'n':
                    flg = False
                    break
                elif your_ans == 'Y':
                    flg = True
                    break
            if flg:
                shutil.move(this_file, this_file.replace(name1, name2))
                print this_file, 'is moved to', this_file.replace(name1, name2)

def find_from_to(str1, start_str, end_str):
    start_num = str1.find(start_str) + len(start_str)
    end_num = str1.find(end_str, start_num)
    return str1[start_num:end_num]

def get_photo(url, fname):
    try:
        urllib.urlretrieve(url, fname)
        urllib.urlcleanup()
        return True
    except IOError:
        return False
    except urllib2.HTTPError:
        return False
    except urllib2.URLError:
        return False
    except httplib.BadStatusLine:
        return False

def get_photos(photos):
    for i in photos:
        threads=[]
        for photo in photos:
            if not 'http' in photo[0]:
                print 'Maybe urls and file names are the opposite. You should switch the indices.'
            t = threading.Thread(target = get_photo,args = (photo[0], photo[1]))
            threads.append(t)
            t.start()

def printr(*targ_str):
    str_to_print = ''
    for temp_str in targ_str:
        str_to_print += str(temp_str) + ' '
    str_to_print = str_to_print[:-1]
    sys.stdout.write(str_to_print + '\r')
    sys.stdout.flush()

def emphasise(*targ_str):
    str_to_print = ''
    for temp_str in targ_str:
        str_to_print += str(temp_str) + ' '
    str_to_print = str_to_print[:-1]
    num_repeat = len(str_to_print) / 2 + 1
    print '＿' + '人' * (num_repeat + 1) + '＿'
    print '＞　%s　＜' % str_to_print
    print '￣' + 'Y^' * num_repeat + 'Y￣'

def mkdir_if_missing(dir_path):
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

def makedirs_if_missing(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def makebsdirs_if_missing(f_path):
    makedirs_if_missing(os.path.dirname(f_path) if '/' in f_path else f_path)

def wait_for(targ_path, wait_sec=3):
    wait_flg = False
    temp_count = 0
    if len(targ_path) > 50:
        targ_path_str = '[...]' + targ_path[-45:]
    else:
        targ_path_str = targ_path
    while not os.path.exists(targ_path):
        printr('waiting for appearing %s (Elapsed : %d sec)' % (targ_path_str, temp_count * wait_sec))
        temp_count += 1
        time.sleep(wait_sec)
        wait_flg = True
    if wait_flg:
        time.sleep(wait_sec)
    elif time.time() - os.path.getmtime(targ_path) < wait_sec:
        time.sleep(wait_sec)

def split_inds(all_num, split_num, split_targ):
    assert split_num >= 1
    assert split_targ >= 0
    assert split_targ < split_num
    part = all_num // split_num
    if not split_num == split_targ+1:
        return split_targ * part, (split_targ+1) * part
    else:
        return split_targ * part, all_num

try:
    import numpy as np
    def are_same_vecs(vec_a, vec_b, this_eps1=1e-5):
        if not vec_a.ravel().shape == vec_b.ravel().shape:
            return False
        if np.linalg.norm(vec_a.ravel()) == 0:
            if not np.linalg.norm(vec_b.ravel()) == 0:
                print 'assertion failed.'
                print 'diff norm : %f' % (np.linalg.norm(vec_a.ravel() - vec_b.ravel()))
                return False
        else:
            if not np.linalg.norm(vec_a.ravel() - vec_b.ravel()) / np.linalg.norm(vec_a.ravel()) < this_eps1:
                print 'assertion failed.'
                print 'diff norm : %f' % (np.linalg.norm(vec_a.ravel() - vec_b.ravel()) / np.linalg.norm(vec_a.ravel()))
                return False
        return True
    def comp_vecs(vec_a, vec_b, this_eps1=1e-5):
        assert are_same_vecs(vec_a, vec_b, this_eps1)
except:
    def comp_vecs(*input1, **input2):
        print 'comp_vecs() cannot be loaded.'
        return

try:
    import Levenshtein
    def search_nn_str(targ_str, str_lists):
        dist = float('inf')
        dist_str = None
        for i in sorted(str_lists):
            cur_dist = Levenshtein.distance(i, targ_str)
            if dist > cur_dist:
                dist = cur_dist
                dist_str = i
        return dist_str
except:
    def search_nn_str(targ_str, str_lists):
        print 'search_nn_str() cannot be imported.'
        return

def flatten(targ_list):
    new_list = copy.deepcopy(targ_list)
    for i in reversed(range(len(new_list))):
        if isinstance(new_list[i], list):
            new_list[i:i+1] = flatten(new_list[i])
    return new_list
# implementing this like stack is ok

def predict_charset (targ_str):
    targ_charsets = ['utf-8', 'cp932', 'euc-jp', 'iso-2022-jp']
    for targ_charset in targ_charsets:
        try:
            targ_str.decode(targ_charset)
            return targ_charset
        except UnicodeDecodeError:
            pass
    return None

def remove_non_ascii(targ_str, charset=None):
    if charset is not None:
        assert isinstance(targ_str, str)
        targ_str = targ_str.decode(charset)
    else:
        assert isinstance(targ_str, unicode)
    return ''.join([x for x in targ_str if ord(x) < 128]).encode('ascii')
