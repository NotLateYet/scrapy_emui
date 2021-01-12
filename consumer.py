# -*- coding: UTF-8 -*-
import sys
from database import ResultDAO, UnFetchDAO
from utils import get_rand_name
from logger import *
from smbtool import *


class IpConsumer(object):
    """
    爬虫消费者类
    """

    def __init__(self, local_password, w3_username, w3_password):
        self.__name = get_rand_name()
        self.logger = Logger('log/consumer_%s.log' % self.__name, level='debug')
        self.logger.info('Create a consumer(%s).' % self.__name)
        self.__smbtool = SmbTool(local_password, w3_username, w3_password)

    def __parse_item(self, parent_path, file_info):
        """
        解析EMUI版本信息，业务强相关，可以重写此函数实现自定义功能
        :param parent_path: 父目录路径
        :param file_info: 当前目录名
        :return: 解析后的EMUI版本信息键值对
        """
        file_name = file_info['file_name']
        split_nos = file_name.split('_')
        if len(split_nos) < 2:
            self.logger.error('Parse BL number info error: %s' % file_info)
            return None

        down_no = split_nos[0].replace('BL', '')
        if not down_no or len(down_no) == 0:
            self.logger.error('Parse BL number info error: %s' % file_info)
            return None

        split_brands = split_nos[1].split(' ')
        if len(split_brands) < 2:
            self.logger.error('Parse brand info error: %s' % file_info)
            return None

        brand = split_brands[0]
        emui_ver = split_brands[1]

        file_info['full_path'] = os.path.join(parent_path, file_name)
        file_info['key'] = down_no
        file_info['emui'] = emui_ver
        file_info['brand'] = brand
        return file_info

    def __save_items(self, items, ip_str):
        """
        解析后的EMUI版本信息items若非空，则保存到MongoDB数据库中
        :param items: 解析后的EMUI版本信息集合
        :param ip_str: 共享服务器IP地址
        """
        if len(items) == 0:
            self.logger.info('Fetch ip %s finish, not found files.' % ip_str)
        else:
            self.logger.info('Updating to MongoDB ...')
            ResultDAO.save_db(items)
            self.logger.info('Update finish')

    def __fetch(self, ip_str):
        """
        基于smbtool获取共享目录信息
        :param ip_str: 共享服务器IP地址
        """
        self.__smbtool.set_host(ip_str)
        shares_list = self.__smbtool.list_root_shares()
        items = []
        for share in shares_list:
            file_path = '\\\\%s\\%s' % (ip_str, share)
            self.logger.info('Fetching file path(%s) ...' % file_path)
            file_infos = self.__smbtool.lsdir(share)
            for file_info in file_infos:
                item = self.__parse_item(file_path, file_info)
                if item is None:
                    continue
                items.append(item)
            self.__save_items(items, ip_str)

    def do(self):
        """
        消费者执行入口，get_host是阻塞队列，若Redis没有数据，会阻塞住。
        使用Ctrl+C结束。
        """
        while True:
            ip_str = UnFetchDAO.get_host()
            self.logger.info('Fetching ip: %s ...' % ip_str)
            self.__fetch(ip_str)


if __name__ == '__main__':
    sys.argv = ['', 'local_password', 'server_username', 'server_password']
    if len(sys.argv) <= 3:
        print('Please input arguments of [Linux password / Server Username / Server Passowrd')
    elif ResultDAO.check_index():
        local_password = sys.argv[1]
        server_username = sys.argv[2]
        server_password = sys.argv[3]
        ipc = IpConsumer(local_password, server_username, server_password)
        ipc.do()
