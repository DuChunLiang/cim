#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import time
import cantools
import can
import binascii


# 日志打印信息
def logger(content, is_file=False, path="./log/monitor_log.log"):
    now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    log_data = '%s - %s' % (now_date, content)
    print(log_data)

    if is_file:
        log_file = open(path, "a")
        log_file.write(log_data)
        log_file.close()


class CPO:
    dbc_id_list = []
    frame_id_dict = {0x0FFF0E01: [0, 0], 0x0FFF0301: [0, 0], 0x0FFF0401: [0, 0], 0x0FFF1401: [0, 0],
                     0x0FFF2401: [0, 0], 0x0FFF0601: [0, 0], 0x0FFF3401: [0, 0]}

    change_frame_list = [0x0FFF0301]
    interval_dict = {}
    last_frame_dict = {}  # 记录上一帧数据用来判断数据变更信息
    error_log_path = "./log/monitor_log.log"
    is_shutdown = False

    frame_timeout = 2500  # 帧发送超时时间(毫秒)

    def __init__(self):
        pass


class Monitor:

    def __init__(self, channel="can0"):
        self.channel = channel
        self.record_count = 0

    # 去掉id的地址信息
    @staticmethod
    def get_source_id(s_id):
        d = bytearray.fromhex("%08X" % s_id)
        d[-1] = d[-1] & 0xF0
        return int(binascii.b2a_hex(d), 16)

    @staticmethod
    def get_hex_str(data):
        return str(binascii.b2a_hex(data))[2:18].upper()

    # 解析can消息
    def analysis_can(self):
        logger("start can monitor...\r\n", True, CPO.error_log_path)

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
                if CPO.is_shutdown:
                    CPO.is_shutdown = False

                frame_id = bo.arbitration_id

                timestamp = bo.timestamp
                data = (bo.data + bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0]))[:8]
                if frame_id in CPO.frame_id_dict:
                    frame_dict = CPO.frame_id_dict[frame_id]

                    # 数据变更和变更范围监控
                    self.frame_data_change(frame_id, data)

                    real_interval = round((timestamp - frame_dict[0]) * 1000, 5)
                    # interval = real_interval
                    frame_dict[0] = timestamp
                    frame_dict[1] = real_interval

                    # print("0x%03X  %s  %s\r\n" % (frame_id, real_interval, real_interval))
                    # 第一次计算间隔时间不准，过滤掉
                    if real_interval < 60 * 10000:

                        if real_interval > CPO.frame_timeout:
                            content = "frame time D-value is too large 0x%03X  %s\r\n" % (frame_id, real_interval)
                            logger(content, True, CPO.error_log_path)

                        # log_content = "0x%03X %03s      %s" % (frame_id, interval,
                        #                                        str(binascii.b2a_hex(data))[1:].upper())
                        # logger(log_content)

    # 数据变更和变更范围监控
    def frame_data_change(self, frame_id, data):
        hex_str_data = self.get_hex_str(data)
        # source_frame_id = self.get_source_id(frame_id)

        if frame_id in CPO.change_frame_list:
            # 判断是否已经存入上次数据的记录字典
            if frame_id not in CPO.last_frame_dict:
                CPO.last_frame_dict[frame_id] = "00"
            else:
                original = CPO.last_frame_dict[frame_id]
                # 判断数据组合是否已经稳定
                if len(original) == len(hex_str_data):
                    # 判断数据是否变化
                    if original != hex_str_data:
                        content = "frame data change 0x%03X original:%s change:%s\r\n" % (frame_id, original,
                                                                                          hex_str_data)
                        logger(content, True, CPO.error_log_path)
                CPO.last_frame_dict[frame_id] = hex_str_data


if __name__ == "__main__":
    Monitor().analysis_can()


