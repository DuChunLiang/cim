#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import time
import cantools
import can
import binascii
import threading
import struct
import mysql_service
from udstools import IsoTp


def logger(content, is_file=False, is_print=True, path="./logs/current_error.log"):
    now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    log_data = '%s - %s\r\n' % (now_date, content)
    if is_print:
        print(log_data)
    if is_file:
        if not os.path.exists("./logs/"):
            os.makedirs("./logs/")

        log_file = open(path, "a")
        log_file.write(log_data)
        log_file.close()


class CPO:
    mysql_support = True
    debug = 0
    dbc_id_list = []  # dbc信息存储 用于判断id是否存在
    out_dict = {}
    env_is_ok = False
    can_addr = 0
    break_time = time.time()
    open_out_time = time.time()
    test_time = time.time()
    error_log_path = "./logs/current_error.log"
    catalina_log_path = "./logs/current_catalina.log"
    run_record = 0
    test_unit_result = ""
    test_unit_fail = ""
    test_state = 0  # 0-成功 1-失败

    out_can_dict = {
        0: b'\x54\x64\x64\x64\x64\xFF\xFF\x01',
        1: b'\x54\x64\x64\x64\x64\xFF\xFF\x02'
    }

    out_ran_dict = {
        "duty1": b'\x01\x23\x54\x64\x64\x64\x64\x64',
        "duty2": b'\x56\x78\x59\x64\x64\x64\x64\x64',
        "duty3": b'\xAB\xCD\x40\x64\x64\x64\x64\x64'
    }

    out_close = b'\x00\x00\x00\x00\x00\x00\x00\x00'

    cur_scope_dict_0 = {"OUT01": [8000, 10000], "OUT02": [8000, 10000], "OUT03": [3500, 5500], "OUT04": [3500, 5500],
                        "OUT05": [3500, 5500], "OUT06": [3500, 5500], "OUT07": [3500, 5500], "OUT08": [3500, 5500],
                        "OUT09": [1500, 2500], "OUT10": [1500, 2500], "OUT11": [1500, 2500], "OUT12": [1500, 2500],
                        "OUT13": [1500, 2500], "OUT14": [1500, 2500], "OUT15": [1500, 2500], "OUT16": [1500, 2500],
                        "OUT17": [1500, 2500], "OUT18": [1500, 2500], "OUT20": [8000, 10000]}

    cur_scope_dict_1 = {"OUT02": [8000, 10000], "OUT03": [3500, 5500], "OUT04": [3500, 5500], "OUT05": [3500, 5500],
                        "OUT06": [3500, 5500], "OUT07": [3500, 5500], "OUT08": [3500, 5500], "OUT09": [1500, 2500],
                        "OUT10": [1500, 2500], "OUT11": [1500, 2500], "OUT12": [1500, 2500], "OUT13": [1500, 2500],
                        "OUT14": [1500, 2500], "OUT15": [1500, 2500], "OUT16": [1500, 2500], "OUT17": [1500, 2500],
                        "OUT18": [1500, 2500], "OUT19": [8000, 10000], "OUT20": [8000, 10000]}


# uds交互服务
class UdsServer:
    def __init__(self, can_bus=None):
        id_source = int("0x0CDA%02XF1" % CPO.can_addr, 16)
        id_target = int("0x0CDAF1%02X" % CPO.can_addr, 16)
        self.tp = IsoTp(can_bus, id_source=id_source, id_target=id_target, extended_id=True)

    @staticmethod
    def str_to_hex(s):
        return ''.join([hex(ord(c)).replace('0x', '') for c in s]).upper()

    @staticmethod
    def bytes_to_hexstr(bytes):
        r = ""
        for b in bytes:
            s = "%02X" % b
            r += s
        return r

    def send(self, data):
        # print("send: ", data)
        self.tp.send_pdu(bytearray.fromhex(data))
        res_data = self.tp.get_pdu()
        # print("result: ", binascii.b2a_hex(res_data))
        time.sleep(0.05)
        return res_data

    def close(self):
        if self.tp is not None:
            self.tp.close()

    # 获取温度
    def get_tem(self):
        # uds协议获取can信息
        res_uds_data = self.send(data="22040408")
        val = round(struct.unpack(">I", res_uds_data[3:7])[0] * 0.1)
        return val

    # 获取im218设备唯一编码
    def get_im218_device_id(self):
        device_id = ""
        try:
            bsp_info = self.bytes_to_hexstr(self.send("22FD05"))[6:]
            iap_info = self.bytes_to_hexstr(self.send("22F181"))[6:]

            if len(iap_info) > 0:
                device_id += bsp_info
            if len(bsp_info) > 0:
                device_id += iap_info
        except Exception as e:
            print(e)
        return device_id


# 解析数据
class Analysis:

    def __init__(self):
        # 加载dbc文件
        self.db = cantools.database.load_file('dbc/IM218.dbc')
        can.rc['interface'] = 'socketcan'
        can.rc['channel'] = sys.argv[1]
        self.can_bus = can.interface.Bus()
        if CPO.mysql_support:
            self.tr = mysql_service.TestReport()  # 初始化添加测试报文服务

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

    def can_send(self, arbitration_id=None, data=None):
        # print("send data: ", binascii.b2a_hex(data))
        try:
            msg = can.Message(arbitration_id=arbitration_id, data=data, extended_id=False)
            self.can_bus.send(msg=msg, timeout=10)
            time.sleep(0.001)
        except Exception as e:
            print("can_send:", e)
            time.sleep(3)

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
                        self.close_all_out()
                    frame_id = self.get_source_id(bo.arbitration_id)
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

                            # print("evn current_val", current_val)
                            record_count += 1
                            if record_count >= 10:
                                # print("%s val=%s" % (index, current_val))
                                if current_val <= 0:
                                    break
                                record_count = 0
                                current_val = 0

    # 检查电流数据是否正确
    @staticmethod
    def check_data(out_key, current_val):
        if CPO.run_record:
            cur_scope_dict = CPO.cur_scope_dict_1
        else:
            cur_scope_dict = CPO.cur_scope_dict_0

        if out_key in cur_scope_dict:
            cur_scope = cur_scope_dict[out_key]
            if int(current_val) < cur_scope[0] or int(current_val) > cur_scope[1]:
                content = "error %s %s[%s %s]" % (out_key, current_val, cur_scope[0], cur_scope[1])
                logger(content=content, is_file=True, is_print=False)
                CPO.test_unit_fail += "%s|%s[%s %s]," % (out_key, current_val, cur_scope[0], cur_scope[1])
                CPO.test_state = 1
            else:
                content = "success %s %s[%s %s]" % (out_key, current_val, cur_scope[0], cur_scope[1])
            logger(content=content, is_file=True, path=CPO.catalina_log_path)
            CPO.test_unit_result += "%s|%s[%s %s]," % (out_key, current_val, cur_scope[0], cur_scope[1])

    # 循环发送占空比
    def send_out_duty(self):
        while True:
            if CPO.env_is_ok:
                for duty in CPO.out_ran_dict.items():
                    can_id = 0x140 + CPO.can_addr
                    self.can_send(arbitration_id=can_id, data=duty[1])
                    time.sleep(0.1)

    # 关闭输出
    def close_all_out(self):
        for i in range(2):
            can_id = 0x0C0 + CPO.can_addr
            self.can_send(arbitration_id=can_id, data=CPO.out_close)
            time.sleep(0.1)

    def close_out1_out19(self):
        for i in range(2):
            can_id = 0x0C0 + CPO.can_addr
            self.can_send(arbitration_id=can_id, data=b'\x54\x64\x64\x64\x64\xFF\xFF\x00')
            time.sleep(0.1)

    # 获取报文中的20路out信息
    def _get_im218_out(self, frame_id=None, data=None):
        frame_id = self.get_source_id(frame_id)
        # print("---%03X" % frame_id)
        if frame_id == 0x300:
            res = self.db.decode_message(frame_id, data)
            if res is not None:
                ledi_ch1_current = int(res['ledi_ch1_current'])
                ledi_ch1_id = int(res['ledi_ch1_id'])
                ledi_ch2_current = int(res['ledi_ch2_current'])
                ledi_ch2_id = int(res['ledi_ch2_id'])
                self._im218_out_val_op(frame_id=frame_id, index=ledi_ch1_id, val=ledi_ch1_current)
                self._im218_out_val_op(frame_id=frame_id, index=ledi_ch2_id, val=ledi_ch2_current)

        elif frame_id == 0x380:
            res = self.db.decode_message(frame_id, data)
            if res is not None:
                out_ch1_id = int(res['out_ch1_id'])
                out_ch2_id = int(res['out_ch2_id'])
                out_ch3_id = int(res['out_ch3_id'])
                out_ch1_value = int(res['out_ch1_value'])
                out_ch2_value = int(res['out_ch2_value'])
                out_ch3_value = int(res['out_ch3_value'])

                self._im218_out_val_op(frame_id=frame_id, index=out_ch1_id, val=out_ch1_value)
                self._im218_out_val_op(frame_id=frame_id, index=out_ch2_id, val=out_ch2_value)
                self._im218_out_val_op(frame_id=frame_id, index=out_ch3_id, val=out_ch3_value)

    # 根据报文的索引值获取输出值
    @staticmethod
    def _im218_out_val_op(frame_id, index, val):
        # print("out---", hex(frame_id), index, val)
        if frame_id == 0x300:
            if index == 1:
                CPO.out_dict['OUT09'] = val
            elif index == 2:
                CPO.out_dict['OUT10'] = val
            elif index == 3:
                CPO.out_dict['OUT11'] = val
            elif index == 4:
                CPO.out_dict['OUT12'] = val
            elif index == 5:
                CPO.out_dict['OUT13'] = val
            elif index == 6:
                CPO.out_dict['OUT14'] = val
            elif index == 7:
                CPO.out_dict['OUT15'] = val
            elif index == 8:
                CPO.out_dict['OUT16'] = val
            elif index == 9:
                CPO.out_dict['OUT17'] = val
            elif index == 10:
                CPO.out_dict['OUT18'] = val
        elif frame_id == 0x380:
            if index == 2:
                CPO.out_dict['OUT02'] = val
            elif index == 3:
                CPO.out_dict['OUT03'] = val
            elif index == 4:
                CPO.out_dict['OUT04'] = val
            elif index == 5:
                CPO.out_dict['OUT05'] = val
            elif index == 6:
                CPO.out_dict['OUT06'] = val
            elif index == 7:
                CPO.out_dict['OUT07'] = val
            elif index == 8:
                CPO.out_dict['OUT08'] = val
            elif index == 10:
                CPO.out_dict['OUT20'] = val
            elif index == 13:
                CPO.out_dict['OUT01'] = val
                CPO.out_dict['OUT19'] = val

    # 检查是否完成接收数据
    @staticmethod
    def check_recv_data():
        result = 0
        # sum_val = 0
        # for o in CPO.out_dict.items():
        #     if int(o[1]) <= 0:
        #         sum_val += 1

        check_time = time.time() - CPO.break_time
        if check_time > 20:
            result = 1
        return result

    # 发送控制
    def send_control(self):
        while True:
            CPO.test_time = time.time()
            CPO.env_is_ok = False
            # 检查测试环境
            self.check_env()
            CPO.env_is_ok = True
            us = UdsServer(can_bus=self.can_bus)  # 初始化uds
            device_id = us.get_im218_device_id()
            print("device_id:", device_id)
            if CPO.mysql_support:
                # 添加测试报告主表信息
                report_id = self.tr.inset_report(device_id=device_id, device_name="IM_218")

            CPO.open_out_time = time.time()
            # 循环不关闭输出测试
            while True:
                CPO.out_dict = {}
                CPO.break_time = time.time()
                data = CPO.out_can_dict[CPO.run_record]
                temperature = us.get_tem()  # 获取温度
                logger(content="send_data: %s %s℃" % (us.bytes_to_hexstr(data), round(us.get_tem(), 2)), is_file=True, path=CPO.catalina_log_path)
                for i in range(2):
                    can_id = 0x0C0 + CPO.can_addr
                    self.can_send(arbitration_id=can_id, data=data)
                    time.sleep(0.1)

                while True:
                    bo = self.can_bus.recv(timeout=5)
                    if bo is not None:
                        if not bo.is_extended_id:
                            # 判断是否有重启或复位
                            if self.get_source_id(bo.arbitration_id) == 0x0:
                                # 检查测试环境
                                self.check_env()
                            else:
                                data = (bo.data + bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0]))[:8]
                                self._get_im218_out(frame_id=bo.arbitration_id, data=data)
                                if self.check_recv_data():
                                    break
                    else:
                        logger(content="can connect error", is_file=True, path=CPO.catalina_log_path)
                        time.sleep(5)
                        break

                # 校验获取电流值
                for key in sorted(CPO.out_dict):
                    val = CPO.out_dict[key]
                    # print("%s %s" % (key, val))
                    self.check_data(key, val)

                # 切换OUT1和OUT19
                if CPO.run_record:
                    CPO.run_record = 0
                else:
                    CPO.run_record = 1

                if CPO.mysql_support:
                    test_unit_name = "IM218-19路输出电流测试"
                    self.tr.insert_report_detail(report_id, temperature, test_unit_name, CPO.test_unit_result, CPO.test_unit_fail)
                    CPO.test_unit_fail = ""
                    CPO.test_unit_result = ""

                if (time.time() - CPO.open_out_time) > 30 * 60:
                    break

            # 关闭输出
            self.close_all_out()
            if CPO.mysql_support:
                self.tr.update_test_time(report_id, (time.time()-CPO.test_time), CPO.test_state)
                CPO.test_state = 0

            logger(content="-------------------complete--------------------", is_file=True, path=CPO.catalina_log_path)
            time.sleep(10 * 60)


if __name__ == "__main__":
    a = Analysis()
    thread_name = "threading-out_duty"
    t_d = threading.Thread(target=a.send_out_duty, name=thread_name)
    t_d.setDaemon(True)

    thread_name = "threading-send_control"
    t_s = threading.Thread(target=a.send_control, name=thread_name)
    t_s.setDaemon(True)

    t_d.start()
    t_s.start()

    t_s.join()





