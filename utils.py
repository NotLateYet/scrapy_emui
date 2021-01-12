import socket
import uuid

ENCODING_FORMAT = 'UTF-8'


def get_hostname():
    return socket.gethostname()


def get_ip():
    return socket.gethostbyname(get_hostname())


def get_uuid():
    return uuid.uuid1().hex


def get_rand_name():
    return get_ip() + "_" + get_uuid()[:6]


def is_ip(ip_str):
    return True
    # p = re.compile("^((?:(2[0-4]\d)|(25[0-5])|([01]?\d\d?))\.){3}(?:(2[0-4]\d)|(255[0-5])|([01]?\d\d?))$")
    # return re.match(p, ip_str)


def ip_2_str(ip):
    return '.'.join([str(i) for i in ip])


def str_2_ip(ip_str):
    return [int(i) for i in ip_str.split('.')]


def str_2_bytes(s):
    return str(s).encode(encoding=ENCODING_FORMAT)


def bytes_2_str(b):
    return bytes(b).decode(encoding=ENCODING_FORMAT)
