import logging
from abc import ABC, abstractmethod
from database import *
from utils import *

logging.basicConfig(level=logging.DEBUG)


class BaseProducer(ABC):
    def __init__(self):
        self.__name = get_rand_name()
        self.logger = logging.getLogger(__name__)
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


class IpProducer(BaseProducer, ABC):
    def __init__(self):
        super(IpProducer, self).__init__()
        self.__key_last = 'last_ip'

    def __loop_ip(self):
        while True:
            ip = DB.redis.hget(self.__key_last, 'ip')
            if ip is not None:
                ip = list(ip)
            else:
                ip = [127, 0, 0, 1]
            nip = next_ip(ip)
            if nip is None:
                return False
            DB.redis.hset(self.__key_last, 'ip', bytes(nip))
            if not ping_ip(ip):
                continue
            self.__loop_dir(ip)

    def __loop_dir(self, ip):
        dirs = ['IT_VMP_SHA_%03d_F']
        reach = []
        unreach = []
        for dir in dirs:
            for i in range(1000):
                d = dir % i
                if len(list_dir(ip, d)) > 0:
                    reach.append(d)
                else:
                    unreach.append(d)
        reach_json = json.dumps({'ip': ip, 'paths': reach})
        unreach_json = json.dumps({'ip': ip, 'paths': unreach})
        DB.redis.rpush(self.key_unreach, unreach_json)
        DB.redis.rpush(self.key_unfetch, reach_json)
        self.logger.debug('Process item: key=%s, value=%s' % (self.key_unreach, unreach_json))
        self.logger.debug('Process item: key=%s, value=%s' % (self.key_unfetch, reach_json))

    def do(self):
        self.__loop_ip()


if __name__ == '__main__':
    ipp = IpProducer()
    ipp.start()
