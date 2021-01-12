# -*- coding: UTF-8 -*-
import os
import subprocess
import tempfile
import time


class SmbTool(object):
    """
    使用smbclient获取共享服务器所共享的根目录以及其子目录。
    注意：当前仅获取了二级目录的目录名、创建时间和修改时间，具体的文件操作暂未支持，因为已经挂在到本地，因此可以像操作本地文件一样进行操作
    """

    def __init__(self, local_password, server_username, server_password, host='', domain='CHINA'):
        # 执行此项目脚本的本地环境密码
        self.__local_password = local_password
        # 共享服务器IP，初始化时可以不设置，后续通过set_host方法设置
        self.__host = host
        # 用于登录共享服务器的用户名
        self.__username = server_username
        # 用于登录共享服务器的密码
        self.__password = server_password
        # 共享服务器所在域
        self.__domain = domain

    @staticmethod
    def shell(cmd):
        """
        用于执行shell命令的独立方法
        :param cmd: shell 命令
        :return: shell命令返回的str格式结果
        """
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        result = process.communicate()[0]
        if result is None:
            return []
        if type(result) is bytes:
            result = str(result, encoding='UTF-8')
        return result.split('\n')

    @staticmethod
    def timestamp_2_time(timestamp):
        """
        时间戳转成datetime格式
        :param timestamp: 时间戳
        :return: datetime格式的字符串
        """
        time_struct = time.localtime(timestamp)
        return time.strftime('%Y-%m-%d %H:%M:%S', time_struct)

    @staticmethod
    def file_create_time(filepath):
        """
        获取目录的创建时间
        :param filepath: 目录全路径
        :return: 目录的创建时间字符串
        """
        t = os.path.getctime(filepath)
        return SmbTool.timestamp_2_time(t)

    @staticmethod
    def file_modify_time(filepath):
        """
        获取目录的修改时间
        :param filepath: 目录全路径
        :return: 目录的修改时间字符串
        """
        t = os.path.getmtime(filepath)
        return SmbTool.timestamp_2_time(t)

    def set_host(self, host):
        """
        实时设置需要访问的共享服务器的IP地址
        :param host: 共享服务器的IP地址
        """
        self.__host = host

    def list_root_shares(self):
        """
        使用smbclient命令获取共享服务器所共享的根目录列表
        :return:
        """
        cmd = 'smbclient -L {0} -U {1}%{2} -W {3}'.format(self.__host, self.__username, self.__password, self.__domain)
        result = SmbTool.shell(cmd)
        if result is None or len(result) == 0:
            return []
        shares_list = []
        for line in result:
            if 'Disk' in line:
                shares_list.append(line.strip().split(' ')[0])
        return shares_list

    def sudo(self):
        """
        获取root权限，因为后续的mount和unmount命令需要root权限
        :return:
        """
        cmd = 'echo %s | sudo -S ls' % self.__local_password
        SmbTool.shell(cmd)

    def mount_dir(self, share_dir, tmp_path):
        """
        挂载共享根目录到本地临时目录
        :param share_dir: 服务器的共享目录
        :param tmp_path: 本地临时目录
        """
        mount_dir_cmd = 'sudo mount -t cifs -o username=%s,password=%s,domain=%s //%s/%s %s'
        SmbTool.shell(
            mount_dir_cmd % (self.__username, self.__password, self.__domain, self.__host, share_dir, tmp_path))

    def unmount_dir(self, tmp_path):
        """
        卸载映射到本地的共享目录，并清理本地临时目录
        :param tmp_path: 本地临时目录
        """
        unmount_dir_cmd = 'sudo umount -a -t cifs -l'
        SmbTool.shell(unmount_dir_cmd)
        SmbTool.shell('sudo rm -fr %s' % tmp_path)

    def lsdir(self, share_dir):
        """
        列出共享根目录下的所有子目录名、创建时间、最后修改时间
        :param share_dir: 共享根目录名
        :return: 共享目录下所有子目录的名称、创建时间、最后修改时间
        """
        tmp_path = tempfile.mkdtemp()
        self.sudo()
        self.mount_dir(share_dir, tmp_path)
        dir_infos = []
        try:
            dir_list = os.listdir(tmp_path)
        except PermissionError:
            dir_list = []

        for dir in dir_list:
            full_path = os.path.join(tmp_path, dir)
            if not os.path.exists(full_path) or not os.path.isdir(full_path):
                continue
            dir_info = {
                'file_name': dir,
                'create_time': SmbTool.file_create_time(full_path),
                'modify_time': SmbTool.file_modify_time(full_path),
            }
            dir_infos.append(dir_info)

        self.unmount_dir(tmp_path)
        return dir_infos


if __name__ == '__main__':
    local_password = 'local_password'
    server_ip = '10.189.12.168'
    server_username = 'server_username'
    server_password = 'server_password'
    domain = 'CHINA'

    smb_tool = SmbTool(local_password, server_username, server_password, server_ip, domain)
    shares_list = smb_tool.list_root_shares()
    for share in shares_list:
        file_info_list = smb_tool.lsdir(share)
        print(file_info_list)
