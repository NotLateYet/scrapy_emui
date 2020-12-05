import logging
import json
import time
from abc import ABC, abstractmethod
from database import *
from utils import *

logging.basicConfig(level=logging.DEBUG)


class BaseConsumer(ABC):
    def __init__(self):
        self.__name = get_rand_name()
        self.logger = logging.getLogger(__name__)
        self.key_unfetch = 'unfetch'
        self.key_fetched = 'fetched'
        self.logger.info('Create a consume(%s).' % self.__name)

    def start(self):
        self.logger.info('Start consume items ...')
        self.do()
        self.logger.info('Consume items end.')

    @abstractmethod
    def do(self):
        pass


class IpConsumer(BaseConsumer, ABC):
    def __init__(self):
        super(IpConsumer, self).__init__()

    def __parse_path(self, file, modify_time):
        split_nos = file.split('_')
        down_no = split_nos[0].replace('BL', '')
        split_brands = split_nos[1].split(' ')
        brand = split_brands[0]
        emui_ver = split_brands[1]
        res = {
            'key': file,
            'modify_time': modify_time,
            'down_no': down_no,
            'brand': brand,
            'emui': emui_ver
        }
        return json.dumps(res)

    def __do_fetch(self, values):
        if 'ip' not in values or 'paths' not in values:
            self.logger.error('Not found ip or paths in %s' % json.dumps(values))
            return False
        ip = values['ip']
        paths = values['paths']
        for path in paths:
            ip_path = concat_ip_path(ip, path)
            for file in list_dir(ip, path):
                if not file.startswith('BL'):
                    continue
                full_path = os.path.join(ip_path, file)
                modify_time = file_create_time(full_path)
                parse_dir = self.__parse_path(file, modify_time)
                DB.redis.rpush(self.key_fetched, parse_dir)

    def do(self):
        while True:
            value = DB.redis.lpop(self.key_unfetch)
            if value is None:
                time.sleep(1)
                logging.info('Task queue is empty. waiting ...')
            else:
                logging.info('Feaching path %s' % value)
                values = json.loads(value)
                self.__do_fetch(values)


if __name__ == '__main__':
    ipp = IpConsumer()
    ipp.start()
