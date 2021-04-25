# sw_autoconf
# version:1.1
# author: zhangzhenhui
# email: 639188185@qq.com


from netmiko import ConnectHandler
import sys,os
from datetime import datetime
import threading
import settings

dev_dict = {}
dev_list = []
dev_map = {}
idc_name = ''
device_type = ''
dev_name =''
host = ''

######Setting maxmun threading number######
threads_max_num = 1    # 配置线上交换机时，建立单线程跑
###########################################

class ConfigSwitch(object):
    def __init__(self):
        if os.path.exists(os.getcwd() + '/command_config_result.txt'):
            os.remove(os.getcwd() + '/command_config_result.txt')
        self.scan_log = open('command_config_result.txt', 'a+')

    def conf_commands(self, dev_map):
        command_list = []
        try:
            self.net_connect = ConnectHandler(**dev_map)
            with open('command_config_file', 'r') as commands:
                for command_line in commands.readlines():
                    command_line = command_line.strip('\n')
                    command_list.append(str(command_line))
            print(command_list)
            print('Device:{0} is Configuring...'.format(dev_map['host']))
            output = self.net_connect.send_config_set(command_list)
            self.scan_log.writelines(output)
            print('Device:{0} is Done.'.format(dev_map['host']))
            print('#####################################')
        except:
            nowtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print('Unable to connect to the switch')
            print('配置执行失败的交换机: {0} {1}'.format(dev_map['host'], nowtime))

def get_dev_info(dev_file):
    dev_files = '/Users/zhangzhenhui/Desktop/python/paramiko/' + idc_name + '_list'
    with open(dev_file, 'r') as devices:
        global dev_dict
        global dev_list
        global device_type
        global dev_map
        global dev_name
        for i in devices:
            block_flag = False
            i = i.split()
            dev_os = i[3]
            dev_role = i[2]
            dev_ip = i[1]
            dev_name = i[0]
            login_port = 22
            login_secret = ''
            login = 'test'  #设备列表文件没有单独的密码的话，会尝试默认账户
            pwd = 'test'
            if len(i) > 4:
                login = i[4]
                pwd = i[5]
            for type in settings.block_role:
                if type in dev_name:
                    block_flag = True
            if not block_flag:
                key_name = ("device_type", "host", "username", "password", "port", "secret")
                values = (dev_os, dev_ip, login, pwd, login_port, login_secret)
                dev_dict = dict(zip(key_name, values))
                dev_list.append(dev_dict)

        threads = []
        n = 1
        for dev_map in dev_list:
            threads.append(threading.Thread(target=ConfigSwitch().conf_commands, args=(dev_map,)))
            if n % threads_max_num == 0:
                for t in threads:
                    t.start()
                for t in threads:
                    t.join()
                threads = []
            n = n + 1
            if n - 1 == len(dev_list):
                for t in threads:
                    t.start()
                for t in threads:
                    t.join()

get_dev_info('/Users/zhangzhenhui/Desktop/python/netmiko_scan/dev_list')

# if __name__ == '__main__':
#     if len(sys.argv) == 2:
#         print("Start Scaning...",datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
#         get_dev_info(sys.argv[1])
#         print("All Done!",datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
