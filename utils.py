import socket
import uuid
import os
import subprocess
import time
import platform

PING_COUNT_PARAM = '-n' if platform.system() == 'Windows' else '-c'
PING_WAIT_PARAM = '-w' if platform.system() == 'Windwos' else '-W'
ENCODING_FORMAT = 'UTF-8'


def get_hostname():
    return socket.gethostname()


def get_ip():
    return socket.gethostbyname(get_hostname())


def get_uuid():
    return uuid.uuid1().hex


def get_rand_name():
    return get_ip() + "_" + get_uuid()[:6]


def ping_ip(ip_str):
    return subprocess.call(['ping', PING_COUNT_PARAM, '2', PING_WAIT_PARAM, '100', ip_str]) == 0


def next_ip(ip_str):
    nip = str_2_ip(ip_str)
    index = 3
    while index >= 0 and nip[index] == 255:
        nip[index] = 1
        index -= 1
    if index == -1:
        return None
    nip[index] += 1
    return ip_2_str(nip)


def concat_ip_path(ip_str, path):
    return '//' + ip_str + '/' + path


def list_dir(ip_str, path):
    try:
        return os.listdir(concat_ip_path(ip_str, path))
    except OSError:
        return []


def timestamp_2_time(timestamp):
    time_struct = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S', time_struct)


def file_create_time(filepath):
    t = os.path.getmtime(filepath)
    return timestamp_2_time(t)


def ip_2_str(ip):
    return '.'.join([str(i) for i in ip])


def str_2_ip(ip_str):
    return [int(i) for i in ip_str.split('.')]


def str_2_bytes(s):
    return str(s).encode(encoding=ENCODING_FORMAT)


def bytes_2_str(b):
    return bytes(b).decode(encoding=ENCODING_FORMAT)
