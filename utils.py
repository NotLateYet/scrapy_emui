import socket
import uuid
import os
import subprocess
import time


def get_hostname():
    return socket.gethostname()


def get_ip():
    return socket.gethostbyname(get_hostname())


def get_uuid():
    return uuid.uuid1().hex


def get_rand_name():
    return get_ip() + "_" + get_uuid()[:6]


def ping_ip(ip):
    return subprocess.call(['ping', '-c', '2', '.'.join([str(i) for i in ip])]) == 0


def next_ip(ip):
    nip = ip.copy()
    index = 3
    while index >= 0 and nip[index] == 255:
        nip[index] = 1
        index -= 1
    if index == -1:
        return None
    nip[index] += 1
    return nip


def concat_ip_path(ip, path):
    ip_str = '.'.join([str(i) for i in ip])
    return '//' + ip_str + '/' + path


def list_dir(ip, path):
    try:
        return os.listdir(concat_ip_path(ip, path))
    except OSError:
        return []


def timestamp_2_time(timestamp):
    time_struct = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S', time_struct)


def file_create_time(filepath):
    t = os.path.getmtime(filepath)
    return timestamp_2_time(t)
