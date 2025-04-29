import os
from types import MappingProxyType

def __init__():
    __exec_dir = os.path.dirname(os.path.abspath(__file__))
    __path = os.path.join(__exec_dir, 'wow.conf')
    l_config = {}
    if os.path.exists(__path):
        with open(__path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        for line in lines:
            line = line.strip()
            if line.find('#') == 0:
                continue
            idx = line.find('=')
            if idx == -1:
                continue
            l_config[line[:idx].strip()] = line[idx + 1:].strip()
    return MappingProxyType(l_config)

config_view = __init__()
