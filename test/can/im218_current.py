#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import time
import cantools
import can
import binascii
import threading


# 日志打印信息
# def logger(content):
#     if CPO.debug:
#         now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
#         print('%s - %s' % (now_date, content))


def logger(content, is_file=False, path="./logs/current_error.log"):
    now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    log_data = '%s - %s\r\n' % (now_date, content)
    print(log_data)
    if is_file:
        if not os.path.exists("./logs/"):
            os.makedirs("./logs/")

        log_file = open(path, "a")
        log_file.write(log_data)
        log_file.close()


class CPO:
    debug = 0
    dbc_id_list = []  # dbc信息存储 用于判断id是否存在
    multiple_list = []
    multiple_count = 0
    multiple_id_180 = []
    multiple_id_300 = []
    multiple_id_380 = []
    complete_package_180 = ""
    complete_package_300 = ""
    complete_package_380 = ""
    env_is_ok = False
    can_addr = 0

    break_time = time.time()
    is_break = False
    op_out = []
    error_log_path = "./logs/current_error.log"
    catalina_log_path = "./logs/current_catalina.log"

    out_can_dict = {
        "out01": [b'\x00\x64\x64\x64\x64\x00\x00\x01', "380_13"], "out02": [b'\x04\x64\x64\x64\x64\x00\x00\x00', "380_2"],
        "out03": [b'\x10\x64\x64\x64\x64\x00\x00\x00', "380_3"], "out04": [b'\x40\x64\x64\x64\x64\x00\x00\x00', "380_4"],
        "out05": [b'\x00\x64\x64\x64\x64\x01\x00\x00', "380_5"], "out06": [b'\x00\x64\x64\x64\x64\x02\x00\x00', "380_6"],
        "out07": [b'\x00\x64\x64\x64\x64\x04\x00\x00', "380_7"], "out08": [b'\x00\x64\x64\x64\x64\x08\x00\x00', "380_8"],
        "out09": [b'\x00\x64\x64\x64\x64\x10\x00\x00', "300_1"], "out10": [b'\x00\x64\x64\x64\x64\x20\x00\x00', "300_2"],
        "out11": [b'\x00\x64\x64\x64\x64\x40\x00\x00', "300_3"], "out12": [b'\x00\x64\x64\x64\x64\x80\x00\x00', "300_4"],
        "out13": [b'\x00\x64\x64\x64\x64\x00\x01\x00', "300_5"], "out14": [b'\x00\x64\x64\x64\x64\x00\x02\x00', "300_6"],
        "out15": [b'\x00\x64\x64\x64\x64\x00\x04\x00', "300_7"], "out16": [b'\x00\x64\x64\x64\x64\x00\x08\x00', "300_8"],
        "out17": [b'\x00\x64\x64\x64\x64\x00\x10\x00', "300_9"], "out18": [b'\x00\x64\x64\x64\x64\x00\x20\x00', "300_10"],
        "out19": [b'\x00\x64\x64\x64\x64\x00\x00\x02', "380_13"], "out20": [b'\x00\x64\x64\x64\x64\x00\x80\x00', "380_10"]
    }

    # 10 12
    out_ran_dict = {
        "out05": b'\x00\x00\x10\x64\x64\x64\x64\x64', "out06": b'\x01\x00\x10\x64\x64\x64\x64\x64',
        "out07": b'\x02\x00\x10\x64\x64\x64\x64\x64', "out08": b'\x03\x00\x10\x64\x64\x64\x64\x64',
        "out09": b'\x04\x00\x10\x64\x64\x64\x64\x64', "out10": b'\x05\x00\x10\x64\x64\x64\x64\x64',
        "out11": b'\x06\x00\x10\x64\x64\x64\x64\x64', "out12": b'\x07\x00\x10\x64\x64\x64\x64\x64',
        "out13": b'\x08\x00\x10\x64\x64\x64\x64\x64', "out14": b'\x09\x00\x10\x64\x64\x64\x64\x64',
        "out15": b'\x0A\x00\x10\x64\x64\x64\x64\x64', "out16": b'\x0B\x00\x10\x64\x64\x64\x64\x64',
        "out17": b'\x0C\x00\x10\x64\x64\x64\x64\x64', "out18": b'\x0D\x00\x10\x64\x64\x64\x64\x64'
    }

    out_close = b'\x00\x00\x00\x00\x00\x00\x00\x00'


class Analysis:

    def __init__(self):
        # 加载dbc文件
        self.cur_val = 800    # 设备电流值(单位 mA) 24V/电阻值*1000
        self.cur_scope = [self.cur_val-100, self.cur_val+100]
        self.db = cantools.database.load_file('dbc/IM218.dbc')
        can.rc['interface'] = 'socketcan'
        can.rc['channel'] = sys.argv[1]
        self.can_bus = can.interface.Bus()

    def log(self, content, timestamp):
        pass

    # 判断id在dbc文件中是否存在
    @staticmethod
    def id_is_exist(_id):
        ret = True if _id in CPO.dbc_id_list else False
        return ret

    # 去掉id的地址信息
    @staticmethod
    def get_source_id(id):
        d = bytearray.fromhex("%04X" % id)
        d[1] = d[1] & 0xF0
        return int(binascii.b2a_hex(d), 16)

    @staticmethod
    def assembly_data(data):
        return [hex(c) for c in data]

    # 获取信号的值范围
    def get_signal_val_range(self, source_frame_id, signal_name):
        msg = self.db.get_message_by_frame_id(source_frame_id)
        signal = msg.get_signal_by_name(signal_name)

        return tuple([signal.minimum, signal.maximum])

    # 根据报文数据检测生成此报文的所有关联ID
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

                CPO.multiple_list = []
                CPO.multiple_count = 0

    # 解析can消息
    def analysis_can(self):
        logger("已启动can数据解析")

        # 存入dbc文件中所有id 用于判断传入id在dbc中是否存在
        for m in self.db.messages:
            CPO.dbc_id_list.append(m.frame_id)

        while True:
            bo = self.can_bus.recv()
            if not bo.is_extended_id:
                frame_id = self.get_source_id(bo.arbitration_id)
                data = (bo.data + bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0]))[:8]
                data_len = bo.dlc

                if len(sys.argv) >= 3:
                    if int(sys.argv[2], 16) != self.get_source_id(bo.arbitration_id):
                        frame_id = 0x100000000

                # 判断id是否存在
                if self.id_is_exist(frame_id):
                    if frame_id == 0x200 or frame_id == 0x280:
                        ifreq_index = 1
                        if frame_id == 0x280:
                            ifreq_index = 2

                        res = self.db.decode_message(frame_id, data)
                        if res is not None:
                            ton_toff_0 = int(res['ifreq%s_ton_toff_1' % ifreq_index])
                            ton_toff_1 = int(res['ifreq%s_ton_toff_2' % ifreq_index])
                            ton_toff_2 = int(res['ifreq%s_ton_toff_3' % ifreq_index])
                            ton_toff_3 = int(res['ifreq%s_ton_toff_4' % ifreq_index])
                            ton_toff_4 = int(res['ifreq%s_ton_toff_5' % ifreq_index])
                            ton_toff_5 = int(res['ifreq%s_ton_toff_6' % ifreq_index])

                            if data_len == 2:
                                ton = ton_toff_0
                                toff = ton_toff_1
                            elif data_len == 4:
                                ton = int("%02X%02X" % (ton_toff_1, ton_toff_0), 16)
                                toff = int("%02X%02X" % (ton_toff_3, ton_toff_2), 16)
                            else:
                                ton = int("%02X%02X%02X" % (ton_toff_2, ton_toff_1, ton_toff_0), 16)
                                toff = int("%02X%02X%02X" % (ton_toff_5, ton_toff_4, ton_toff_3), 16)
                            content = "%s ton=%s, toff=%s" % (hex(bo.arbitration_id), str(ton), str(toff))
                            self.log(content, bo.timestamp)
                    elif frame_id == 0x180:
                        res = self.db.decode_message(frame_id, data)
                        if res is not None:
                            ch1_id = int(res['ch1_id'])
                            ch1_value = int(res['ch1_value'])
                            ch2_id = int(res['ch2_id'])
                            ch2_value = int(res['ch2_value'])
                            ch3_id = int(res['ch3_id'])
                            ch3_value = int(res['ch3_value'])
                            ch4_id = int(res['ch4_id'])
                            ch4_value = int(res['ch4_value'])

                            pack_data = ""
                            if ch1_id > 0:
                                pack_data += "{id:%s value:%s}" % (ch1_id, ch1_value)
                            if ch2_id > 0:
                                pack_data += "{id:%s value:%s}" % (ch2_id, ch2_value)
                            if ch3_id > 0:
                                pack_data += "{id:%s value:%s}" % (ch3_id, ch3_value)
                            if ch4_id > 0:
                                pack_data += "{id:%s value:%s}" % (ch4_id, ch4_value)

                            if len(CPO.multiple_id_180) == 0:
                                self.create_multiple_id(ch1_id, frame_id)
                            else:

                                if ch1_id == CPO.multiple_id_180[0]:
                                    CPO.complete_package_180 = ""
                                    CPO.complete_package_180 += pack_data
                                elif ch1_id != CPO.multiple_id_180[len(CPO.multiple_id_180) - 1]:
                                    CPO.complete_package_180 += pack_data
                                else:
                                    CPO.complete_package_180 += pack_data

                                    content = "0x%03X %s" % (bo.arbitration_id, CPO.complete_package_180)
                                    self.log(content, bo.timestamp)

                    elif frame_id == 0x300:
                        res = self.db.decode_message(frame_id, data)
                        if res is not None:
                            # val_range = self.get_signal_val_range(frame_id, "ledi_ch1_current")
                            # print('--', val_range)

                            ledi_ch1_current = int(res['ledi_ch1_current'])
                            ledi_ch1_id = "300_%s" % res['ledi_ch1_id']
                            # ledi_ch1_voltage = int(res['ledi_ch1_voltage'])
                            ledi_ch2_current = int(res['ledi_ch2_current'])
                            ledi_ch2_id = "300_%s" % res['ledi_ch2_id']
                            # ledi_ch2_voltage = int(res['ledi_ch2_voltage'])

                            current_val = 0
                            index = CPO.op_out[1]
                            if ledi_ch1_id == index:
                                current_val = ledi_ch1_current
                            elif ledi_ch2_id == index:
                                current_val = ledi_ch2_current

                            # if current_val > 0:
                            print("%s val: %s" % (CPO.op_out, current_val))
                            if current_val > 0:
                                CPO.is_break = True

                    elif frame_id == 0x380:
                        res = self.db.decode_message(frame_id, data)
                        if res is not None:
                            out_ch1_id = "380_%s" % res['out_ch1_id']
                            out_ch2_id = "380_%s" % res['out_ch2_id']
                            out_ch3_id = "380_%s" % res['out_ch3_id']
                            out_ch1_value = int(res['out_ch1_value'])
                            out_ch2_value = int(res['out_ch2_value'])
                            out_ch3_value = int(res['out_ch3_value'])

                            current_val = 0

                            # out = CPO.op_out[0]
                            index = CPO.op_out[1]
                            if out_ch1_id == index:
                                current_val = out_ch1_value
                            elif out_ch2_id == index:
                                current_val = out_ch2_value
                            elif out_ch3_id == index:
                                current_val = out_ch3_value

                            # print(out_ch1_id, out_ch1_value, out_ch2_id, out_ch2_value, out_ch3_id, out_ch3_value)
                            print("%s val: %s" % (CPO.op_out, current_val))
                            if current_val > 0:
                                CPO.is_break = True

                    elif frame_id == 0x100:
                        res = self.db.decode_message(frame_id, data)
                        # for r in dict(res).items():
                        #     print(r)
                        if res is not None:
                            ana1 = int(res['ana1'])
                            ana2 = int(res['ana2'])

                            content = "0x%03X ana1=%s, ana2=%s" % (bo.arbitration_id, ana1, ana2)
                            self.log(content, bo.timestamp)

                    elif frame_id == 0x400:
                        res = self.db.decode_message(frame_id, data)
                        if res is not None:
                            sens1_inf = int(res['sens1_inf'])
                            sens2_inf = int(res['sens2_inf'])
                            wiper_Fail = int(res['wiper_fail'])
                            oilavl = int(res['oilavl'])
                            Vbat_inf = int(res['vbat_inf'])
                            V1_inf = int(res['v1_inf'])
                            V2_inf = int(res['v2_inf'])

                            content = "0x%03X sens1_inf=%s, sens1_inf=%s, " \
                                      "sens1_inf=%s, sens1_inf=%s, " \
                                      "sens1_inf=%s, sens1_inf=%s, " \
                                      "sens1_inf=%s" % (bo.arbitration_id, sens1_inf, sens2_inf, wiper_Fail,
                                                        oilavl, Vbat_inf, V1_inf, V2_inf)

                            self.log(content, bo.timestamp)
                    elif frame_id == 0x80:
                        res = self.db.decode_message(frame_id, data)
                        if res is not None:
                            content = "0x%03X wk1_state=%s, wk2_state=%s, icu1_bool=%s, icu1_inf=%s," \
                                      "icu2_bool=%s, icu2_inf=%s, hb1_bool=%s, " \
                                      "hb1_inf=%s, hb2_bool=%s, hb2_inf=%s, hb3_bool=%s, " \
                                      "hb3_inf=%s, hb4_bool=%s, hb4_inf=%s, out5_bool=%s, out5_inf=%s, " \
                                      "out6_bool=%s, out6_inf=%s, out7_bool=%s, out7_inf=%s, out8_bool=%s, out8_inf=%s, " \
                                      "out9_bool=%s, out9_inf=%s, out10_bool=%s, out10_inf=%s, out11_bool=%s, " \
                                      "out11_inf=%s, out12_bool=%s, out12_inf=%s, out13_bool=%s, out13_inf=%s, " \
                                      "out14_bool=%s, out14_inf=%s, out15_bool=%s, out15_inf=%s, " \
                                      "out16_bool=%s, out16_inf=%s, out17_bool=%s, out17_inf=%s, " \
                                      "out18_bool=%s, out18_inf=%s, out19_bool=%s, out19_inf=%s, " \
                                      "out20_bool=%s, out20_inf=%s, ana1_bool=%s, ana1_inf=%s, ana2_bool=%s, ana2_inf=%s," \
                                      "uin1_bool=%s, uin1_inf=%s, uin2_bool=%s, uin2_inf=%s, uin3_bool=%s, uin3_inf=%s, " \
                                      "uin4_bool=%s, uin4_inf=%s, uin5_bool=%s, uin5_inf=%s, uin6_bool=%s, uin6_inf=%s, " \
                                      "uin7_bool=%s, uin7_inf=%s" % (bo.arbitration_id, res['wk1_state'],
                                                                     res['wk2_state'], res['icu1_bool'], res['icu1_inf'],
                                                                     res['icu2_bool'], res['icu2_inf'], res['hb1_bool'],
                                                                     res['hb1_inf'], res['hb2_bool'], res['hb2_inf'],
                                                                     res['hb3_bool'], res['hb3_inf'], res['hb4_bool'],
                                                                     res['hb4_inf'], res['out5_bool'], res['out5_inf'],
                                                                     res['out6_bool'], res['out6_inf'], res['out7_bool'],
                                                                     res['out7_inf'], res['out8_bool'], res['out8_inf'],
                                                                     res['out9_bool'], res['out9_inf'], res['out10_bool'],
                                                                     res['out10_inf'], res['out11_bool'],
                                                                     res['out11_inf'],
                                                                     res['out12_bool'], res['out12_inf'],
                                                                     res['out13_bool'],
                                                                     res['out13_inf'], res['out14_bool'],
                                                                     res['out14_inf'],
                                                                     res['out15_bool'], res['out15_inf'],
                                                                     res['out16_bool'],
                                                                     res['out16_inf'], res['out17_bool'],
                                                                     res['out17_inf'],
                                                                     res['out18_bool'], res['out18_inf'],
                                                                     res['out19_bool'],
                                                                     res['out19_inf'], res['out20_bool'],
                                                                     res['out20_inf'],
                                                                     res['ana1_bool'], res['ana1_inf'], res['ana2_bool'],
                                                                     res['ana2_inf'], res['uin1_bool'], res['uin1_inf'],
                                                                     res['uin2_bool'], res['uin2_inf'], res['uin3_bool'],
                                                                     res['uin3_inf'], res['uin4_bool'], res['uin4_inf'],
                                                                     res['uin5_bool'], res['uin5_inf'], res['uin6_bool'],
                                                                     res['uin6_inf'], res['uin7_bool'], res['uin7_inf'],)
                            self.log(content, bo.timestamp)

                # else:
                #     print('-------%s在dbc文件中不存在-------' % frame_id)

    def can_send(self, arbitration_id=None, data=None):
        # print("send data: ", binascii.b2a_hex(data))
        try:
            msg = can.Message(arbitration_id=arbitration_id, data=data, extended_id=False)
            self.can_bus.send(msg=msg, timeout=10)
            time.sleep(0.001)
        except Exception as e:
            print("can_send:", e)

    # 检查测试环境是否满足
    def check_env(self):
        logger(content="check test env...", is_file=True, path=CPO.catalina_log_path)
        record_count = 0
        current_val = 0
        while True:
            bo = self.can_bus.recv()
            if bo is not None:
                if not bo.is_extended_id:
                    CPO.can_addr = bo.arbitration_id & 0xF
                    if record_count == 0:
                        self.close_out()
                    frame_id = self.get_source_id(bo.arbitration_id)
                    # print("----%03X" % bo.arbitration_id)
                    data = (bo.data + bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0]))[:8]
                    # 判断是否有重启或复位
                    if frame_id == 0x0:
                        # 启动模块
                        self.can_send(arbitration_id=0x040, data=b'\x01')
                        time.sleep(0.5)
                        self.can_send(arbitration_id=0x040, data=b'\x07')
                        time.sleep(0.5)
                    elif frame_id == 0x380:
                        res = self.db.decode_message(frame_id, data)
                        if res is not None:
                            out_ch1_id = "380_%s" % res['out_ch1_id']
                            out_ch2_id = "380_%s" % res['out_ch2_id']
                            out_ch3_id = "380_%s" % res['out_ch3_id']
                            out_ch1_value = int(res['out_ch1_value'])
                            out_ch2_value = int(res['out_ch2_value'])
                            out_ch3_value = int(res['out_ch3_value'])

                            # out_key = CPO.op_out[0]
                            index = "380_13"
                            if out_ch1_id == index:
                                current_val += out_ch1_value
                            elif out_ch2_id == index:
                                current_val += out_ch2_value
                            elif out_ch3_id == index:
                                current_val += out_ch3_value

                            record_count += 1
                            if record_count >= 10:
                                # print("%s val=%s" % (index, current_val))
                                if current_val <= 0:
                                    break
                                record_count = 0
                                current_val = 0

    # 检查电流数据是否正确
    def check_data(self, out_key, current_val):
        if int(current_val) < self.cur_scope[0] or int(current_val) > self.cur_scope[1]:
            content = "error %s %s[%s %s]" % (out_key, current_val, self.cur_scope[0], self.cur_scope[1])
            # logger(content=content, is_file=True)
        else:
            content = "success %s %s[%s %s]" % (out_key, current_val, self.cur_scope[0], self.cur_scope[1])
        logger(content=content, is_file=True, path=CPO.catalina_log_path)

    # 循环发送占空比
    def send_out_duty(self):
        while True:
            if CPO.env_is_ok:
                for duty in CPO.out_ran_dict.items():
                    can_id = 0x140 + CPO.can_addr
                    self.can_send(arbitration_id=can_id, data=duty[1])
                    time.sleep(0.1)

    # 关闭输出
    def close_out(self):
        for i in range(2):
            can_id = 0x0C0 + CPO.can_addr
            self.can_send(arbitration_id=can_id, data=CPO.out_close)
            time.sleep(0.1)

    # 发送控制
    def send_control(self):
        while True:
            CPO.env_is_ok = False
            # 检查测试环境
            self.check_env()
            print("check_env success")
            CPO.env_is_ok = True
            for out_key in sorted(CPO.out_can_dict):
                CPO.break_time = time.time()
                CPO.op_out = [out_key, CPO.out_can_dict[out_key][1]]
                data = CPO.out_can_dict[out_key][0]
                CPO.is_break = False
                for i in range(2):
                    can_id = 0x0C0 + CPO.can_addr
                    self.can_send(arbitration_id=can_id, data=data)
                    time.sleep(0.1)
                recv_count = 1
                recv_max_val = 0
                while True:
                    bo = self.can_bus.recv(timeout=5)
                    if bo is not None:
                        if not bo.is_extended_id:
                            frame_id = self.get_source_id(bo.arbitration_id)
                            data = (bo.data + bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0]))[:8]
                            # 判断是否有重启或复位
                            if frame_id == 0x0:
                                # 检查测试环境
                                self.check_env()
                            elif frame_id == 0x300:
                                res = self.db.decode_message(frame_id, data)
                                if res is not None:
                                    ledi_ch1_current = int(res['ledi_ch1_current'])
                                    ledi_ch1_id = "300_%s" % res['ledi_ch1_id']
                                    # ledi_ch1_voltage = int(res['ledi_ch1_voltage'])
                                    ledi_ch2_current = int(res['ledi_ch2_current'])
                                    ledi_ch2_id = "300_%s" % res['ledi_ch2_id']
                                    # ledi_ch2_voltage = int(res['ledi_ch2_voltage'])

                                    out_key = CPO.op_out[0]
                                    current_val = 0
                                    index = CPO.op_out[1]
                                    if ledi_ch1_id == index:
                                        current_val = ledi_ch1_current
                                    elif ledi_ch2_id == index:
                                        current_val = ledi_ch2_current

                                    if current_val > 0 or (time.time() - CPO.break_time) > 3:
                                        # print("recv_count:", recv_count)
                                        # print("%s val: %s" % (CPO.op_out, current_val))
                                        if current_val > recv_max_val:
                                            recv_max_val = current_val

                                        if recv_count > 3 or (time.time() - CPO.break_time) > 5:
                                            self.check_data(out_key, recv_max_val)
                                            break

                                        recv_count += 1

                            elif frame_id == 0x380:
                                res = self.db.decode_message(frame_id, data)
                                if res is not None:
                                    out_ch1_id = "380_%s" % res['out_ch1_id']
                                    out_ch2_id = "380_%s" % res['out_ch2_id']
                                    out_ch3_id = "380_%s" % res['out_ch3_id']
                                    out_ch1_value = int(res['out_ch1_value'])
                                    out_ch2_value = int(res['out_ch2_value'])
                                    out_ch3_value = int(res['out_ch3_value'])

                                    current_val = 0

                                    out_key = CPO.op_out[0]
                                    index = CPO.op_out[1]
                                    if out_ch1_id == index:
                                        current_val = out_ch1_value
                                    elif out_ch2_id == index:
                                        current_val = out_ch2_value
                                    elif out_ch3_id == index:
                                        current_val = out_ch3_value

                                    if current_val > 0 or (time.time() - CPO.break_time) > 3:
                                        # print("recv_count:", recv_count)
                                        # print("%s val: %s" % (CPO.op_out, current_val))
                                        if current_val > recv_max_val:
                                            recv_max_val = current_val

                                        if recv_count > 3 or (time.time() - CPO.break_time) > 5:
                                            self.check_data(out_key, recv_max_val)
                                            break

                                        recv_count += 1
                    else:
                        logger(content="can connect error", is_file=True, path=CPO.catalina_log_path)
                        time.sleep(5)
                        break

                # if out_key == "out%s" % sys.argv[2]:
                # time.sleep(3)

                # 关闭输出
                self.close_out()

            logger(content="-----------------------complete------------------------", is_file=True, path=CPO.catalina_log_path)
            time.sleep(0.5)


if __name__ == "__main__":
    a = Analysis()
    # a.analysis_can()
    # a.send_control()

    thread_name = "threading-out_duty"
    t_d = threading.Thread(target=a.send_out_duty, name=thread_name)
    t_d.setDaemon(True)

    thread_name = "threading-send_control"
    t_s = threading.Thread(target=a.send_control, name=thread_name)
    t_s.setDaemon(True)

    t_d.start()
    t_s.start()

    t_s.join()





