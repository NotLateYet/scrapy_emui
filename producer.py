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

    def __loop_ip(self):
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
            self.logger.info('Processing ip: %s' % ip_str)
            if not ping_ip(ip_str):
                continue
            self.__loop_dir(ip_str)

    def __loop_dir(self, ip_str):
        dirs = ['IT_VMP_SHA_%d_F', 'IT_VMP_WHU_%d_F', 'IT_VMP_SIA_%d_F', 'IT_VMP_PEK_%d_F', 'T_VMP_WHU_%d_F']
        reach = []
        unreach = []
        for dir in dirs:
            for i in range(1000):
                d = dir % i
                if len(list_dir(ip_str, d)) > 0:
                    reach.append(d)
                else:
                    unreach.append(d)
        if len(reach) > 0:
            reach_json = json.dumps({'ip': ip_str, 'paths': reach})
            DB.redis.rpush(self.key_unfetch, str_2_bytes(reach_json))
            self.logger.debug('Process [%s] items: %s' % (self.key_unfetch, reach_json))
        if len(unreach) > 0:
            unreach_json = json.dumps({'ip': ip_str, 'paths': unreach})
            DB.redis.rpush(self.key_unreach, str_2_bytes(unreach_json))
            self.logger.debug('Process [%s] items: %s' % (self.key_unreach, unreach_json))

    def do(self):
        self.__loop_ip()


if __name__ == '__main__':
    ipp = IpProducer()
    ipp.start()
