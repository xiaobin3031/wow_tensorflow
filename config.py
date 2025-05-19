#! /usr/bin/python3.12

import os, platform
from types import MappingProxyType

system_name = platform.system().lower()
if system_name == 'linux':
    if 'microsoft' in platform.platform().lower():
        system_name = 'wsl'

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
            key = line[:idx].strip()
            value = line[idx + 1:].strip()
            set_by_system(l_config, key, value)
    return MappingProxyType(l_config)

def set_by_system(config, key, value):
    """
    根据系统，设置属性
    """
    if "." in key:
        idx = key.find('.')
        sys_name = key[:idx].lower()
        if sys_name == system_name:
            key = key[idx+1:]
        else:
            return
    config[key] = value

def get_root_path():
    return config_view['collect_file_root']

def model_path():
    return config_view['model_path']

def ocr_img_size():
    return int(config_view['ocr_img_size'])

config_view = __init__()
