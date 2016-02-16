#!/usr/bin/env python
# -*- coding:utf-8 -*-
from mytoolbox import *
from settings import *
import commands
import time
import datetime

def get_gpu_info(server_name, targ_com, targ_keys):
    gpu_strs = commands.getoutput(COM_SSH % (server_name, targ_com)).split('\n')
    gpu_info_list = []
    if len(gpu_strs) == 1 and gpu_strs[0] == '':
        return gpu_info_list
    for gpu_str in gpu_strs:
        gpu_str = gpu_str.split(', ')
        try:
            assert len(gpu_str) == len(targ_keys)
            gpu_info_list.append(dict([(i, j) for i, j in zip(targ_keys, gpu_str)]))
        except:
            print 'An exception :', server_name, targ_com, targ_keys
            gpu_info_list.append(dict([(i, 'error') for i in targ_keys]))
    return gpu_info_list

def get_gpu_util(server_name):
    return get_gpu_info(server_name, COM_GPU_UTIL, GPU_UTIL_KEYS)

def get_gpu_process(server_name):
    return get_gpu_info(server_name, COM_GPU_PROCESS, GPU_PROCESS_KEYS)

# deprecated
def get_process_user(server_name, pid):
    return commands.getoutput(COM_SSH % (server_name, COM_PROCESS_INFO % (str(pid), str(pid)))).lstrip().split(' ')[1]

def get_process_users(server_name, pids):
    assert isinstance(pids, list)
    if len(pids) == 0:
        return [], []
    no_dup_pids = list(set(pids))
    no_dup_info = commands.getoutput(COM_SSH % (server_name, COM_ALL_PROCESS_INFO % (','.join([str(pid) for pid in no_dup_pids])))).split('\n')
    pid2user = dict([(i, j.split(' ')[0]) for i, j in zip(no_dup_pids, no_dup_info)])
    pid2lstart = dict([(i, ' '.join(j.split(' ')[1:])) for i, j in zip(no_dup_pids, no_dup_info)])
    try:
        users = [pid2user[pid] for pid in pids]
        assert len(users) == len(pids)
        lstarts = [pid2lstart[pid] for pid in pids]
        assert len(lstarts) == len(pids)
    except:
        users   = [0] * len(pids)
        lstarts = [0] * len(pids)
        for num, pid in enumerate(pids):
            lstarts[num] = '-'
            try:
                users[num] = get_process_user(server_name, str(pid))
            except:
                users[num] = 'unknown'
    return users, lstarts

def get_server_info(server_name):
    gpu_util = get_gpu_util(server_name)
    gpu_processes = get_gpu_process(server_name)
    uuid2id = dict([(gpu['uuid'], gpu['id']) for gpu in gpu_util])
    users, lstarts = get_process_users(server_name, [ps['pid'] for ps in gpu_processes])
    if len(gpu_util) == 0 or len(gpu_processes) == 0:
        return gpu_util, gpu_processes, 'TimeOut'
    for ind, user, lstart in zip(range(len(users)), users, lstarts):
        try:
            gpu_processes[ind]['gpu_id'] = uuid2id[gpu_processes[ind]['uuid']]
            gpu_processes[ind]['user']   = user
            gpu_processes[ind]['lstart'] = lstart
        except KeyError:
            return gpu_util, [], 'KeyError'
    return gpu_util, gpu_processes, ''

def get_all_gpu_info():
    server_dic = {}
    d = datetime.datetime.today()
    server_dic['__LASTUPDATED__'] = d.strftime("%x %X")
    server_dic['__INTERVAL__'] = SLEEP
    for ts in TARG_SERVERS:
        server_dic[ts] = {i:j for i, j in zip(['GPUs', 'processes', 'ErrorType'], get_server_info(ts))}
        if ts in PERSONAL_SERVERS.keys():
            server_dic[ts]['Owner'] = PERSONAL_SERVERS[ts]
        else:
            server_dic[ts]['Owner'] = ''
        print ts
    print
    print 'LAST UPDATED:', server_dic['__LASTUPDATED__']
    return server_dic

def main():
    makebsdirs_if_missing(JSON_PATH)
    while True:
        try:
            all_info = get_all_gpu_info()
        except:
            all_info = get_all_gpu_info()
        jsondump(JSON_PATH, all_info)
        time.sleep(SLEEP)
    return

if __name__ == '__main__':
    main()
