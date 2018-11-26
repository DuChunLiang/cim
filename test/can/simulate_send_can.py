#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
import time
# import cantools
import can
# import binascii


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
        can.rc['channel'] = sys.argv[1]
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
        msg = can.Message(arbitration_id=module[0], data=data[0:module[1]], extended_id=False)
        return msg

    def send_can(self, msg):
        self.can_bus.send(msg)
        # logger(msg)

    def start(self):
        while True:
            CPO.recode_count += 10

            if CPO.recode_count % self.interval_millisecond == 0:
                for f_m in self.front_module:
                    if f_m[1] == 8:
                        self.send_can(self.get_message(f_m))

                for a_m in self.after_module:
                    if a_m[1] == 8:
                        self.send_can(self.get_message(a_m))

            if CPO.recode_count % 1000 == 0:
                self.send_can(self.get_message(self.front_module[0]))
                self.send_can(self.get_message(self.after_module[0]))

            time.sleep(0.01)


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        Send().start()
    else:
        logger("Please set can channel")
