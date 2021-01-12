# -*- coding: UTF-8 -*-
from nmap import nmap
from database import UnScanDAO, DB, UnFetchDAO
from utils import *
from logger import *
from config import *


class IpProducer(object):
    """
    生产者类，主要两个用途：
    1. 若Redis中未扫描IP地址为空，则根据指定的起止地址生成IP列表(前三段)，并push到Redis
    2. 若Redis中未扫描IP地址不为空，则获取IP地址并扫描(遍历第四段时，每次从1-255)，然后把扫描到的可连通的IP地址push到Redis
    """

    def __init__(self):
        self.__name = get_rand_name()
        self.__begin = []
        self.__end = []
        self.__nmap = nmap.PortScanner()
        self.logger = Logger('log/producer_%s.log' % self.__name, level='debug')
        self.logger.info('Create a producer(%s)' % self.__name)

    def __scan_ip_subnet__(self, ip3):
        """
        扫描IP段，第四段从1-255遍历
        :param ip3: 包含前三段的未扫描IP地址
        :return: 可连通的IP地址
        """
        self.logger.info('Scanning host(%s.1-255) ... ' % ip3)
        subnet = '{0}.1-255'.format(ip3)
        args = '-sn -PS -T5 --min-parallelism {0}'.format(ScanConfig.CONCURRENT)
        self.__nmap.scan(subnet, arguments=args)
        return self.__nmap.all_hosts()

    def do(self, begin, end):
        """
        生产者功能入口
        :param begin: 用户输入开始IP地址
        :param end: 用户输入结束IP地址
        """
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
                    self.logger.info('Find activate hosts: %s' % alive_hosts)
                    UnFetchDAO.put_hosts(alive_hosts)


if __name__ == '__main__':
    ipp = IpProducer()
    ipp.do('10.0.0.1', '10.255.255.255')
