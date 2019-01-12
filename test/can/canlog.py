#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
import time
import can
import binascii
import struct


# 日志打印信息
def logger(content):
    path = "candump-%s.log" % time.strftime('%Y-%m-%d', time.localtime(time.time()))
    now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    log_data = '%s %s' % (now_date, content)
    # print(log_data)
    log_file = open(path, "a")
    log_file.write(log_data)
    log_file.close()


class CanLog:
    def __init__(self):
        can.rc['interface'] = 'socketcan'
        can.rc['channel'] = sys.argv[1]
        self.can_bus = can.interface.Bus()

    # 去掉id的地址信息
    @staticmethod
    def get_source_id(id):
        d = bytearray.fromhex("%04X" % id)
        d[1] = d[1] & 0xF0
        return int(binascii.b2a_hex(d), 16)

    def start(self):
        while True:
            bo = self.can_bus.recv()
            if not bo.is_extended_id:
                frame_id = self.get_source_id(bo.arbitration_id)
                data = bo.data
                if frame_id == 0x100:
                    ain1 = int(struct.unpack("<H", data[0:2])[0] * 0.05)
                    ain2 = int(struct.unpack("<H", data[2:4])[0] * 0.05)
                    print(ain1, ain2)
                    # logger("%s %03X#%s\r\n" % ("can0", frame_id, str(binascii.b2a_hex(data)).upper()))


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        CanLog().start()
    else:
        logger("Please set can channel")
