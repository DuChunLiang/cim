#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import time
import cantools
import can
import binascii


# 日志打印信息
def logger(content, is_file=False, path="./log/log.log"):
    now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    log_data = '%s - %s' % (now_date, content)
    # print(log_data)

    if is_file:
        log_file = open(path, "a")
        log_file.write(log_data)
        log_file.close()


class CPO:
    multiple_list = []
    multiple_count = 0
    multiple_pack_140 = ""
    dbc_id_list = []
    frame_id_dict = {}
    temp_dict = {}
    interval_dict = {}
    last_frame_dict = {}    # 记录上一帧数据用来判断数据变更信息
    start_time = time.time()
    check_time = 5
    reset_time = time.time()
    is_reset = False
    reset_op = True
    is_shutdown = False
    is_record_frame = False
    error_log_path = "./log/error.log"
    interval_log_path = "./log/interval.log"

    frame_timeout = 10  # 帧发送超时时间(毫秒)

    # multiplex_frame_record_dict = {}
    multiple_id_140 = []
    multiplex_frame = [0x180, 0x300, 0x380, 0x140]
    # 判断变更帧
    change_frame = [0x080, 0x400, 0x0C0, 0x1C0, 0x140]

    def __init__(self):
        pass


class Monitor:

    def __init__(self, channel="can0"):
        self.channel = channel
        self.record_count = 0
        self.dbc_path = "dbc/IM218.dbc"
        # 加载dbc文件
        self.db = cantools.database.load_file(self.dbc_path)

    # 去掉id的地址信息
    @staticmethod
    def get_source_id(s_id):
        d = bytearray.fromhex("%04X" % s_id)
        d[1] = d[1] & 0xF0
        return int(binascii.b2a_hex(d), 16)

    @staticmethod
    def record_frame(frame_id):
        if frame_id not in CPO.temp_dict:
            CPO.temp_dict[frame_id] = [0, 0, 0]  # [毫秒数，间隔发送时间， 复用帧的标记ID(非复用帧为0)]
        if (time.time() - CPO.start_time) > CPO.check_time:
            CPO.frame_id_dict = CPO.temp_dict.copy()

    # 智能化处理间隔毫秒数信息
    @staticmethod
    def handle_interval(interval):
        if interval < 10:
                interval = 10
        else:
            position = interval % 10
            if position < 5:
                interval -= position
            else:
                interval += (10 - position)
        return interval

    # 获取复用帧的标识ID
    @staticmethod
    def get_frame_mark_id(res, frame_id):
        mark_id = 0
        if frame_id == 0x180:
            mark_id = int(res['ch1_id'])
        elif frame_id == 0x300:
            mark_id = int(res['ledi_ch1_id'])
        elif frame_id == 0x380:
            mark_id = int(res['out_ch1_id'])
        elif frame_id == 0x140:
            mark_id = int(res['combine_index_0'])
        return mark_id

    @staticmethod
    def create_multiple_id(multiple_id, frame_id):
        if multiple_id not in CPO.multiple_list:
            CPO.multiple_list.append(multiple_id)
        else:
            CPO.multiple_count += 1
            if CPO.multiple_count >= 10:
                if frame_id == 0x300:
                    CPO.multiple_id_300 = CPO.multiple_list.copy()
                elif frame_id == 0x380:
                    CPO.multiple_id_380 = CPO.multiple_list.copy()
                elif frame_id == 0x140:
                    CPO.multiple_id_140 = CPO.multiple_list.copy()

                CPO.multiple_list = []
                CPO.multiple_count = 0

    @staticmethod
    def get_hex_str(data):
        return str(binascii.b2a_hex(data))[2:18].upper()

    # 解析can消息
    def analysis_can(self):
        logger("start can monitor...")

        # 存入dbc文件中所有id 用于判断传入id在dbc中是否存在
        for m in self.db.messages:
            CPO.dbc_id_list.append(m.frame_id)

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
                source_frame_id = self.get_source_id(frame_id)
                timestamp = bo.timestamp
                data = (bo.data + bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0]))[:8]

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
                    # 判断是否更换了硬件设备 发送不同的报文
                    if frame_id in CPO.frame_id_dict:
                        # 数据变更和变更范围监控
                        self.frame_data_change(frame_id, data)
                        frame_dict = CPO.frame_id_dict[frame_id]

                        if CPO.is_reset:
                            CPO.is_reset = False
                            logger("system restart successfully\r\n", True, CPO.error_log_path)

                        # 添加复用帧识别ID
                        if source_frame_id in CPO.multiplex_frame:
                            res = self.db.decode_message(source_frame_id, data)
                            if frame_dict[2] == 0:
                                frame_dict[2] = self.get_frame_mark_id(res, source_frame_id)
                                continue
                            else:
                                if frame_dict[2] != self.get_frame_mark_id(res, source_frame_id):
                                    continue

                        real_interval = (timestamp - frame_dict[0]) * 1000
                        interval = self.handle_interval(round(real_interval))
                        frame_dict[0] = timestamp
                        frame_dict[1] = interval

                        # 第一次计算价格时间不准，过滤掉
                        if interval < 60 * 10000:
                            key = "%s_%s" % (frame_id, interval)

                            # 获取dbc中此帧规定的发送间隔时间（毫秒）
                            cycle_time = self.db.get_message_by_frame_id(source_frame_id).cycle_time
                            if cycle_time is not None:
                                d_value = abs(int(cycle_time) - real_interval)
                                print("0x%03X" % frame_id, cycle_time, round(real_interval, 3), d_value)
                                if d_value > CPO.frame_timeout:
                                    content = "frame time is too large 0x%03X  %s %s %s\r\n" % (frame_id,
                                                                                                cycle_time,
                                                                                                real_interval,
                                                                                                d_value)
                                    logger(content, True, CPO.error_log_path)

                            # log_content = "0x%03X %03s      %s" % (frame_id, interval,
                            #                                        str(binascii.b2a_hex(data))[1:].upper())
                            # logger(log_content)

                            CPO.interval_dict[key] = [frame_id, interval, self.get_hex_str(data)]
                            if len(CPO.interval_dict) >= len(CPO.frame_id_dict):
                                content = ""
                                for f_key in sorted(CPO.interval_dict):
                                    content += "0x%03X %03s %s\r\n" % (CPO.interval_dict[f_key][0],
                                                                       CPO.interval_dict[f_key][1],
                                                                       CPO.interval_dict[f_key][2])
                                content += "\r\n\r\n\r\n"
                                log_file = open(CPO.interval_log_path, "w")
                                log_file.write(content)
                                log_file.close()
                    else:
                        # 重新初始化记录的报文ID信息
                        CPO.frame_id_dict = {}
                        self.record_count = 0
                        CPO.interval_dict = {}

    # 数据变更和变更范围监控
    def frame_data_change(self, frame_id, data):
        if self.get_source_id(frame_id) in CPO.multiplex_frame:
            # 判断是否监控个变化， 否则监控值范围
            if self.get_source_id(frame_id) in CPO.change_frame:
                res = self.db.decode_message(self.get_source_id(frame_id), data)
                if res is not None:
                    if self.get_source_id(frame_id) == 0x140:
                        combine_index_0 = int(res['combine_index_0'])

                        data_id_list = CPO.multiple_id_140

                        if len(data_id_list) == 0:
                            self.create_multiple_id(combine_index_0, self.get_source_id(frame_id))
                        else:
                            data_str = self.get_hex_str(data)
                            if combine_index_0 == data_id_list[0]:
                                CPO.multiple_pack_140 = ""
                                CPO.multiple_pack_140 += data_str
                            elif combine_index_0 != data_id_list[len(data_id_list) - 1]:
                                CPO.multiple_pack_140 += data_str
                            else:
                                CPO.multiple_pack_140 += data_str

                                if frame_id in CPO.last_frame_dict:
                                    original = CPO.last_frame_dict[frame_id]
                                    now_data = CPO.multiple_pack_140

                                    # print(hex(frame_id), original, now_data)

                                    if original != now_data:
                                        content = "frame data change original:%s change:%s\r\n" % (original, now_data)
                                        logger(content, True, CPO.error_log_path)

                                CPO.last_frame_dict[frame_id] = CPO.multiple_pack_140

        else:
            if frame_id in CPO.last_frame_dict:
                # 判断是否监控个变化， 否则监控值范围
                if self.get_source_id(frame_id) in CPO.change_frame:
                    original = CPO.last_frame_dict[frame_id]
                    now_data = self.get_hex_str(data)
                    # print(hex(frame_id), original, now_data)
                    if original != now_data:
                        content = "frame data change original:%s change:%s\r\n" % (original, now_data)
                        logger(content, True, CPO.error_log_path)

            CPO.last_frame_dict[frame_id] = self.get_hex_str(data)


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        Monitor(sys.argv[1]).analysis_can()
    else:
        logger("Please set can channel")
