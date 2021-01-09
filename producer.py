from database import *
from utils import *
from logger import *
from config import *
from nmap import nmap


class UnScanDAO(object):
    @staticmethod
    def ip_range(start_str, end_str, length):
        start_int = int(ip_address(start_str).packed.hex(), 16)
        end_int = int(ip_address(end_str).packed.hex(), 16)
        range_end_int = min(end_int, start_int + length)
        return [ip_address(ip).exploded for ip in range(start_int, range_end_int)]

    @staticmethod
    def emtpy():
        return DB.redis.llen(RedisKey.UNSCAN_IP) == 0

    @staticmethod
    def get_range(length):
        pipe = DB.redis.pipeline()
        pipe.lrange(RedisKey.UNSCAN_IP, 0, length - 1)
        pipe.ltrim(RedisKey.UNSCAN_IP, length, -1)
        result = pipe.execute()
        if result is None:
            return None
        return [str(ip, encoding='utf8') for ip in result[0]]

    @staticmethod
    def put_range(start, end, length):
        start_str = '0.' + ip_2_str(start[:3])
        end_str = '0.' + ip_2_str(end[:3])
        if start_str == end_str:
            range_strs = [start_str]
        else:
            range_strs = UnScanDAO.ip_range(start_str, end_str, length)
        if len(range_strs) == 0:
            return
        ip3_range_list = [str(ip_str).lstrip('0.') for ip_str in range_strs]
        pipe = DB.redis.pipeline()
        for ip3_str in ip3_range_list:
            pipe.rpush(RedisKey.UNSCAN_IP, bytes(ip3_str, encoding='utf8'))
        pipe.execute()


class IpProducer(object):
    def __init__(self):
        self.__name = get_rand_name()
        self.__begin = []
        self.__end = []
        self.__nmap = nmap.PortScanner()
        self.logger = Logger('log/producer_%s.log' % self.__name, level='debug')
        self.logger.info('Create a producer(%s)' % self.__name)

    def __scan_ip_subnet__(self, ip3):
        subnet = '{0}.1-255'.format(ip3)
        args = '-sn -PS -T5 --min-parallelism {0}'.format(ScanConfig.CONCURRENT)
        self.__nmap.scan(subnet, arguments=args)
        return self.__nmap.all_hosts()

    def do(self, begin, end):
        if not is_ip(begin) or not is_ip(end):
            self.logger.error('begin(%s) or end(%s) ip is invalid.' % (begin, end))
            return
        self.__begin = str_2_ip(begin)
        self.__end = str_2_ip(end)

        while True:
            with DB.redis_lock.create_lock(RedisKey.LOCK):
                if UnScanDAO.emtpy():
                    UnScanDAO.put_range(self.__begin, self.__end, RedisConfig.PRODUCER_PUT_BATCH)
                ip_batches = UnScanDAO.get_range(RedisConfig.PRODUCER_GET_BATCH)

                if ip_batches is None or len(ip_batches) == 0:
                    self.logger.info('Empty task list. begin ip: %s, end ip: %s' % (begin, end))
                    break

                if UnScanDAO.emtpy():
                    UnScanDAO.put_range(str_2_ip(ip_batches[-1]), self.__end, RedisConfig.PRODUCER_PUT_BATCH)

            for ip in ip_batches:
                alive_hosts = self.__scan_ip_subnet__(ip)
                if len(alive_hosts) > 0:
                    UnFetchDAO.put_hosts(alive_hosts)


if __name__ == '__main__':
    ipp = IpProducer()
    ipp.do('192.168.43.1', '192.168.43.255')
