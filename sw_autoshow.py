# sw_autoshow
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
c_list = []

######################
threads_max_num = 10
######################

class ConfigSwitch(object):
    def __init__(self):
        if os.path.exists(os.getcwd() + '/command_show_result.txt'):
            os.remove(os.getcwd() + '/command_show_result.txt')
        self.scan_log = open('command_show_result.txt', 'a+')

    def show_commands(self, dev_map):
        try:
            self.net_connect = ConnectHandler(**dev_map)
            # print('Device:{0} is show infomation... Please wait'.format(dev_map['host']))
            # output = self.net_connect.send_command('dis cur int lo 0')
            with open('command_show_file', 'r') as command_lists:
                for i in command_lists:
                    output = self.net_connect.send_command(i)
                    print('\n#########################\ndevice: {0}\ncommand: {1}\n{2}\n#########################\n'.format(dev_map['host'], i, output))
                    # print('Device:{0} is Done.'.format(dev_map['host']))
        except:
            nowtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print('Unable to connect to the switch')
            print('show执行失败的交换机: {0} {1}'.format(dev_map['host'], nowtime))

def get_dev_info(dev_file):
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
            threads.append(threading.Thread(target=ConfigSwitch().show_commands, args=(dev_map, )))
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

get_dev_info('/Users/zhangzhenhui/Desktop/python/netmiko_scan/dc01_rsw_list')

# if __name__ == '__main__':
#     if len(sys.argv) == 2:
#         print("Start Scaning...",datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
#         get_dev_info(sys.argv[1])
#         print("All Done!",datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
