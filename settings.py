# settings

# seconds
SLEEP = 300
COMMON_SERVERS = [
    '192.168.174.1', # IPs
    '192.168.174.2',
    '192.168.174.3',
    'tanaka', # domain names are also OK
    'suzuki'
]

# path to save json file that has information of results
JSON_PATH = 'page/gpu_state.json'

# somebody's servers (don't care if all servers are common ones)
# PERSONAL_SERVERS = {
#     '192.168.174.4': 'sato',
#     'goromaru': 'goromaru',
# }
PERSONAL_SERVERS = {}

TARG_SERVERS = COMMON_SERVERS + PERSONAL_SERVERS.keys()


# commands
# COM_SSH = 'ssh %s "%s"'
COM_SSH = 'timeout 10 ssh %s "%s"'
COM_GPU_UTIL = 'nvidia-smi --query-gpu=index,name,uuid,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits'
GPU_UTIL_KEYS = ['id', 'name', 'uuid', 'used_memory', 'total_memory', 'gpu_usage']
COM_GPU_PROCESS = 'nvidia-smi --query-compute-apps=gpu_uuid,pid,used_gpu_memory --format=csv,noheader,nounits'
GPU_PROCESS_KEYS = ['uuid', 'pid', 'gpu_memory']
COM_PROCESS_INFO = 'top -p %s -n 1 -b  | grep %s' #deprecated
COM_ALL_PROCESS_INFO = 'ps -o user:20,lstart -p %s h'
