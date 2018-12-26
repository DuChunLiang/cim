#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
import time
# import cantools
import can
import threading


# 日志打印信息
def logger(content):
    now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    log_data = '%s - %s' % (now_date, content)
    print(log_data)


class CPO:
    recode_count = 0
    dbc_id_list = []


class Send:
    def __init__(self):
        self.interval_millisecond = 500
        if len(sys.argv) >= 3:
            self.interval_millisecond = int(sys.argv[2])

        can.rc['interface'] = 'socketcan'
        can.rc['channel'] = "can0"
        self.can_bus = can.interface.Bus()

        # 前模块帧
        self.front_module = [[0x0FFF0E03, 1], [0x0FFF0303, 8], [0x0FFF0503, 8], [0x0FFF0703, 8],
                             [0x0FFF0903, 8], [0x0FFF1303, 8], [0x0FFF1503, 8], [0x0FFF1703, 8],
                             [0x0FFF1903, 8], [0x0FFF2303, 8]]
        # 后模块帧
        self.after_module = [[0x0FFF0E07, 1], [0x0FFF0307, 8], [0x0FFF0507, 8], [0x0FFF0707, 8],
                             [0x0FFF0907, 8], [0x0FFF1307, 8], [0x0FFF1507, 8], [0x0FFF1707, 8],
                             [0x0FFF1907, 8], [0x0FFF2307, 8]]

    def get_message(self, module):
        data = b"\x00\x00\x00\x00\x00\x00\x00\x00"
        msg = can.Message(arbitration_id=module[0], data=data[0:module[1]])
        return msg

    def send_can(self, msg):
        self.can_bus.send(msg)
        time.sleep(0.001)
        # logger(msg)

    def send_heart(self):
        while True:
            self.send_can(self.get_message(self.front_module[0]))
            self.send_can(self.get_message(self.after_module[0]))
            time.sleep(1)

    def send_data(self):
        while True:
            for f_m in self.front_module:
                if f_m[1] == 8:
                    self.send_can(self.get_message(f_m))

            for a_m in self.after_module:
                if a_m[1] == 8:
                    self.send_can(self.get_message(a_m))

            time.sleep((self.interval_millisecond - 2) * 0.001)

    def start(self):
        thread_name = "threading-heart"
        t_heart = threading.Thread(target=self.send_heart, name=thread_name)
        t_heart.setDaemon(True)

        thread_name = "threading-data"
        t_data = threading.Thread(target=self.send_data, name=thread_name)
        t_data.setDaemon(True)

        t_heart.start()
        t_data.start()

        t_heart.join()


if __name__ == "__main__":
    Send().start()

