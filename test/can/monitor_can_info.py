#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import time
import cantools
import can
import binascii


# 日志打印信息
def logger(content, is_file=False, path="./logs/monitor_log.log"):
    now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    log_data = '%s - %s' % (now_date, content)
    print(log_data)

    if is_file:
        log_file = open(path, "a")
        log_file.write(log_data)
        log_file.close()


class CPO:
    dbc_id_list = []
    frame_id_dict = {}
    temp_dict = {0x100: [0, 0, 0], 0x300: [0, 0, 0]}
    interval_dict = {}
    last_frame_dict = {}  # 记录上一帧数据用来判断数据变更信息
    start_time = time.time()
    check_time = 5
    reset_time = time.time()
    is_reset = False
    reset_op = True
    is_shutdown = False
    is_record_frame = False
    error_log_path = "./logs/monitor_error.log"
    interval_log_path = "./logs/monitor_interval.log"
    catalina_log_path = "./logs/monitor_catalina.log"

    frame_timeout = 50  # 帧发送超时时间(毫秒)

    multiplex_frame_record_dict = {}
    multiplex_frame = [0x180, 0x300, 0x380, 0x140]
    # 判断变更帧
    change_frame = [0x080, 0x400, 0x0C0, 0x1C0, 0x140]
    # 需要监控间隔时间的报文
    limit_op_dict = [0x400, 0x080, 0x100, 0x300, 0x380]

    def __init__(self):
        pass


class Monitor:

    def __init__(self, channel="can0"):
        self.channel = channel
        self.record_count = 0
        self.dbc_path = "dbc/IM218.dbc"
        # 加载dbc文件
        self.db = cantools.database.load_file(self.dbc_path)
        # 存入dbc文件中所有id 用于判断传入id在dbc中是否存在
        for m in self.db.messages:
            CPO.dbc_id_list.append(m.frame_id)

    # 去掉id的地址信息
    @staticmethod
    def get_source_id(s_id):
        can_add = s_id & 0xF
        return s_id - can_add

    # 记录当前收到的报文ID
    def record_frame(self, frame_id):
        # print("frame_id---%03X" % frame_id)
        frame_id = self.get_source_id(frame_id)
        if frame_id in CPO.limit_op_dict:
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
    def get_frame_mark_id(res, source_frame_id):
        mark_id = 0
        if source_frame_id == 0x180:
            mark_id = int(res['ch1_id'])
        elif source_frame_id == 0x300:
            mark_id = int(res['ledi_ch1_id'])
        elif source_frame_id == 0x380:
            mark_id = int(res['out_ch1_id'])
        elif source_frame_id == 0x140:
            mark_id = int(res['combine_index_0'])
        return mark_id

    # 获取信号的值范围
    def get_signal_val_range(self, source_frame_id, signal_name):
        msg = self.db.get_message_by_frame_id(source_frame_id)
        signal = msg.get_signal_by_name(signal_name)
        return tuple([int(signal.minimum), int(signal.maximum)])

    @staticmethod
    def get_hex_str(data):
        return str(binascii.b2a_hex(data))[2:18].upper()

    # 解析can消息
    def analysis_can(self):
        logger("start can monitor...\r\n", True, CPO.catalina_log_path)

        can.rc['interface'] = 'socketcan'
        can.rc['channel'] = self.channel
        can_bus = can.interface.Bus()

        while True:
            bo = can_bus.recv(timeout=10)
            if bo is None:
                if not CPO.is_shutdown:
                    logger("system crash\r\n", True, CPO.catalina_log_path)
                    CPO.is_shutdown = True
            else:
                frame_id = bo.arbitration_id
                source_frame_id = self.get_source_id(frame_id)

                # 判断是否有重启或复位
                if source_frame_id == 0x0:
                    if time.time() - CPO.reset_time > 5:
                        logger("system restart not active...\r\n", True, CPO.catalina_log_path)
                        CPO.is_reset = True
                        CPO.reset_time = time.time()
                        CPO.is_record_frame = False
                        CPO.frame_id_dict = {}
                        self.record_count = 0
                else:
                    if CPO.is_shutdown:
                        CPO.is_shutdown = False

                if len(CPO.frame_id_dict) == 0:
                    if not CPO.is_record_frame:
                        CPO.start_time = time.time()
                        CPO.is_record_frame = True

                    self.record_frame(frame_id)
                    if self.record_count == 0:
                        logger('Initializing frame information, Wait 5 seconds...', True, CPO.catalina_log_path)
                        self.record_count = 1
                else:

                    # print("CPO.dbc_id_list", CPO.dbc_id_list, source_frame_id)
                    # 判断是否在dbc文件内
                    if source_frame_id in CPO.dbc_id_list:
                        timestamp = bo.timestamp
                        data = (bo.data + bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0]))[:8]

                        # 判断是否更换了硬件设备 发送不同的报文
                        if source_frame_id in CPO.frame_id_dict:
                            frame_dict = CPO.frame_id_dict[source_frame_id]

                            if CPO.is_reset:
                                CPO.is_reset = False
                                logger("system restart successfully\r\n", True, CPO.catalina_log_path)

                            # 数据变更和变更范围监控
                            # self.frame_data_change(frame_id, data, frame_dict[2])

                            # 添加复用帧识别ID
                            if source_frame_id in CPO.multiplex_frame:
                                res = self.db.decode_message(source_frame_id, data)
                                if frame_dict[2] == 0:
                                    frame_dict[2] = self.get_frame_mark_id(res, source_frame_id)
                                    continue
                                else:
                                    if frame_dict[2] != self.get_frame_mark_id(res, source_frame_id):
                                        continue

                            real_interval = round((timestamp - frame_dict[0]) * 1000, 5)
                            interval = self.handle_interval(round(real_interval))
                            frame_dict[0] = timestamp
                            frame_dict[1] = interval

                            # 第一次计算间隔时间不准，过滤掉
                            if interval < 60 * 10000:
                                key = "%s_%s" % (source_frame_id, interval)

                                # 获取dbc中此帧规定的发送间隔时间（毫秒）
                                cycle_time = self.db.get_message_by_frame_id(source_frame_id).cycle_time
                                if cycle_time is not None:
                                    d_value = abs(int(cycle_time) - real_interval)
                                    # print("0x%03X" % frame_id, cycle_time, round(real_interval, 3), d_value)
                                    if d_value > CPO.frame_timeout:
                                        content = "frame time D-value is too large 0x%03X  %s %s %s\r\n" % (frame_id,
                                                                                                            cycle_time,
                                                                                                            real_interval,
                                                                                                            d_value)
                                        logger(content, True, CPO.error_log_path)

                                CPO.interval_dict[key] = [source_frame_id, interval, self.get_hex_str(data)]
                                if len(CPO.interval_dict) >= len(CPO.frame_id_dict):
                                    content = ""
                                    for f_key in sorted(CPO.interval_dict):
                                        now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                                        content += "%s - 0x%03X %03s %s\r\n" % (now_date, CPO.interval_dict[f_key][0],
                                                                                CPO.interval_dict[f_key][1],
                                                                                CPO.interval_dict[f_key][2])
                                    content += "\r%s\r\n\r\n" % len(CPO.frame_id_dict)
                                    log_file = open(CPO.interval_log_path, "w")
                                    log_file.write(content)
                                    log_file.close()

                                    if len(CPO.interval_dict) > len(CPO.frame_id_dict):
                                        CPO.interval_dict = {}
                        # else:
                        #     # 重新初始化记录的报文ID信息
                        #     CPO.frame_id_dict = {}
                        #     self.record_count = 0
                        #     CPO.interval_dict = {}
                    # self.record_count += 1

    # 数据变更和变更范围监控
    def frame_data_change(self, frame_id, data, source_mark_id):
        hex_str_data = self.get_hex_str(data)
        source_frame_id = self.get_source_id(frame_id)
        # 判断是不是监控值变化，否则是监控值范围
        if source_frame_id in CPO.change_frame:
            # 判断是否已经存入上次数据的记录字典
            if frame_id not in CPO.last_frame_dict:
                CPO.last_frame_dict[frame_id] = "00"
            else:
                original = CPO.last_frame_dict[frame_id]
                if source_frame_id in CPO.multiplex_frame:
                    if source_mark_id != 0:
                        res = self.db.decode_message(source_frame_id, data)
                        mark_id = self.get_frame_mark_id(res, source_frame_id)
                        if mark_id == source_mark_id:
                            if frame_id in CPO.multiplex_frame_record_dict:
                                now_data = CPO.multiplex_frame_record_dict[frame_id]
                                # 判断数据组合是否已经稳定
                                if len(original) == len(now_data):
                                    # 判断数据是否变化
                                    if original != now_data:
                                        content = "frame data change 0x%03X original:%s change:%s\r\n" \
                                                  % (frame_id, original, now_data)
                                        logger(content, True, CPO.error_log_path)

                                CPO.last_frame_dict[frame_id] = CPO.multiplex_frame_record_dict[frame_id]
                                CPO.multiplex_frame_record_dict[frame_id] = hex_str_data
                        else:
                            if frame_id in CPO.multiplex_frame_record_dict:
                                CPO.multiplex_frame_record_dict[frame_id] += hex_str_data
                            else:
                                CPO.multiplex_frame_record_dict[frame_id] = hex_str_data

                else:
                    # 判断数据组合是否已经稳定
                    if len(original) == len(hex_str_data):
                        # 判断数据是否变化
                        if original != hex_str_data:
                            content = "frame data change 0x%03X original:%s change:%s\r\n" % (frame_id, original,
                                                                                              hex_str_data)
                            logger(content, True, CPO.error_log_path)
                    CPO.last_frame_dict[frame_id] = hex_str_data

        else:
            # 根据dbc文件的设定信号的值范围判断获取的值是否超限
            res = self.db.decode_message(source_frame_id, data)
            if res is not None:
                for r in dict(res).items():
                    signal_name = r[0]
                    signal_val = int(r[1])
                    signal_range = self.get_signal_val_range(source_frame_id, signal_name)
                    s_min = signal_range[0]
                    s_max = signal_range[1]
                    if signal_val < s_min or signal_val > s_max:
                        content = "value out of bounds 0x%03X [%s|%s] %s:%s data:%s\r\n" % (frame_id,
                                                                                            s_min, s_max,
                                                                                            signal_name,
                                                                                            signal_val,
                                                                                            hex_str_data)
                        logger(content, True, CPO.error_log_path)


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        Monitor(sys.argv[1]).analysis_can()
    else:
        logger("Please set can channel")
