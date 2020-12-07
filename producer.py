import json
from abc import ABCMeta, abstractmethod
from database import *
from utils import *
from logger import *


class BaseProducer(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.__name = get_rand_name()
        self.logger = Logger('log/producer_%s.log' % self.__name, level='debug')
        self.key_unfetch = 'unfetch'
        self.key_unreach = 'unreach'
        self.logger.info('Create a producer(%s).' % self.__name)

    def start(self):
        self.logger.info('Start produce items ...')
        self.do()
        self.logger.info('Produce items end.')

    @abstractmethod
    def do(self):
        pass


class IpProducer(BaseProducer):
    def __init__(self):
        super(IpProducer, self).__init__()
        self.__key_last = 'last_ip'
        self.__start_ip_str = '127.0.0.1'

    def __loop_ip(self, ip_str):
        ip = str_2_ip(ip_str)
        for i in range(1, 256):
            ip[3] = i
            tmp_ip = ip_2_str(ip)
            self.logger.info('Processing ip: %s' % tmp_ip)
            db_key = self.key_unfetch if ping_ip(tmp_ip) else self.key_unreach
            DB.redis.rpush(db_key, str_2_bytes(tmp_ip))

    def do(self):
        while True:
            ip_str = DB.redis.hget(self.__key_last, 'ip')
            if ip_str is None:
                ip_str = self.__start_ip_str
            else:
                ip_str = bytes_2_str(ip_str)
            nip_str = next_ip(ip_str)
            if nip_str is None:
                return False
            DB.redis.hset(self.__key_last, 'ip', str_2_bytes(nip_str))
            self.__loop_ip(ip_str)


if __name__ == '__main__':
    ipp = IpProducer()
    ipp.start()
