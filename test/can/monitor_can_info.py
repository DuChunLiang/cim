#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import time
# import cantools
import can
import binascii


# 日志打印信息
def logger(content, is_file=False, path="./log/log.log"):
    now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    log_data = '%s - %s' % (now_date, content)
    print(log_data)
    # print(content)
    if is_file:
        log_file = open(path, "a")
        log_file.write(log_data)
        log_file.close()


class CPO:
    frame_id_dict = {}
    temp_dict = {}
    interval_dict = {}
    start_time = time.time()
    check_time = 5
    reset_time = time.time()
    is_reset = False
    reset_op = True
    is_shutdown = False
    is_record_frame = False
    error_log_path = "./log/error.log"
    interval_log_path = "./log/interval.log"

    def __init__(self):
        pass


class Monitor:

    def __init__(self, channel="can0"):
        self.channel = channel
        self.record_count = 0

    # 去掉id的地址信息
    def get_source_id(self, id):
        d = bytearray.fromhex("%04X" % id)
        d[1] = d[1] & 0xF0
        return int(binascii.b2a_hex(d), 16)

    def record_frame(self, frame_id):
        if frame_id not in CPO.temp_dict:
            CPO.temp_dict[frame_id] = [0, 0]
        if (time.time() - CPO.start_time) > CPO.check_time:
            CPO.frame_id_dict = CPO.temp_dict.copy()

    # 解析can消息
    def analysis_can(self):
        logger("start can monitor...")

        can.rc['interface'] = 'socketcan'
        can.rc['channel'] = self.channel
        can_bus = can.interface.Bus()

        while True:
            bo = can_bus.recv(timeout=10)
            if bo is None:
                if not CPO.is_shutdown:
                    logger("system crash\r\n", True, CPO.error_log_path)
                    CPO.is_shutdown = True
            else:
                frame_id = bo.arbitration_id
                timestamp = bo.timestamp
                data = bo.data
                logger(frame_id)
                # 判断是否有重启或复位
                if frame_id == 0x001 or frame_id == 0x0cda01f1 or frame_id == 0x040:
                    if time.time() - CPO.reset_time > 5:
                        logger("system restart not active...\r\n", True, CPO.error_log_path)
                        CPO.is_reset = True
                        CPO.reset_time = time.time()
                else:
                    if CPO.is_shutdown:
                        CPO.is_shutdown = False

                    if len(CPO.frame_id_dict) == 0:
                        if not CPO.is_record_frame:
                            CPO.start_time = time.time()
                            CPO.is_record_frame = True

                        self.record_frame(frame_id)
                        if self.record_count == 0:
                            logger("Initializing frame information, Wait 5 seconds...")
                            self.record_count = 1
                    else:
                        if frame_id in CPO.frame_id_dict:
                            if CPO.is_reset:
                                CPO.is_reset = False
                                logger("system restart successfully\r\n", True, CPO.error_log_path)

                            frame_dict = CPO.frame_id_dict[frame_id]
                            interval = round((timestamp - frame_dict[0]) * 1000)
                            frame_dict[0] = timestamp
                            frame_dict[1] = interval
                            # print(timestamp, frame_id, data)

                            log_content = "0x%03X %03s      %s" % (frame_id, interval, str(binascii.b2a_hex(data))[1:].upper())
                            logger(log_content)

                            if interval < 60 * 60 * 1000:
                                key = "%s_%s" % (frame_id, interval)
                                CPO.interval_dict[key] = "0x%03X %03s %s" % (frame_id,
                                                                             interval, str(binascii.b2a_hex(data))[1:].upper())

                                if len(CPO.interval_dict) >= len(CPO.frame_id_dict):
                                    content = ""
                                    for f_key in sorted(CPO.interval_dict):
                                        content += "%s\r\n" % CPO.interval_dict[f_key]
                                    content += "\r\n\r\n\r\n\r\n\r\n"
                                    log_file = open(CPO.interval_log_path, "w")
                                    log_file.write(content)
                                    log_file.close()
                                    # CPO.interval_dict = {}


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        Monitor(sys.argv[1]).analysis_can()
    else:
        logger("Please set can channel")


