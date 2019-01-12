#!/usr/bin/env python

import sys
import getopt
import os
import can
import time
import struct
# import binascii
from udstools import IsoTp


# uds发送相关报文
class SendMsg:
    ecu_address = "22FD01"  # 获取ecu地址
    logic_input_status = "22FD02"  # 逻辑输入报文
    app_info = "22FD02"  # 获取app信息
    boot_info = "22F180"  # 获取boog信息
    iap_info = "22F181"  # 获取iap信息
    bsp_info = "22FD05"  # 获取bsp信息
    bridge_status = "22FD04"  # 获取bridge状态
    bridge_current = "22FD08"  # 获取bridge电流
    power_on_Var_Value = "22FD09"  # 获取Poweron变量值
    get_mio_value = "22%s"  # 获取模拟量值
    output_on = "2F%s03"
    output_off = "2F%s030000"
    # frame_dict = {"0100": "OUT1|MC06XS4200BFK|U4", "0101": "OUT2|MC06XS4200BFK|U4",
    #               "0102": "OUT3|MC10XS4200BFK|U6", "0103": "OUT4|MC10XS4200BFK|U6",
    #               "0104": "OUT5|MC10XS4200BFK|U9", "0105": "OUT6|MC10XS4200BFK|U9",
    #               "0106": "OUT7|MC10XS4200BFK|U5", "0107": "OUT8|MC10XS4200BFK|U5",
    #               "0108": "OUT9|MC10XS4200BFK|U8", "0109": "OUT10|MC10XS4200BFK|U8",
    #               "010A": "OUT11|MC10XS4200BFK|U7", "010B": "OUT12|MC10XS4200BFK|U7",
    #               "010C": "OUT13|MC10XS4200BFK|U15", "010D": "OUT14|MC10XS4200BFK|U15",
    #               "010E": "OUT15|MC10XS4200BFK|U16", "010F": "OUT16|MC10XS4200BFK|U16",
    #               "0110": "OUT17|MC10XS4200BFK|U18", "0111": "OUT18|MC10XS4200BFK|U18",
    #               "0112": "OUT19|MC10XS4200BFK|U19", "0113": "OUT20|MC10XS4200BFK|U19",
    #               "0201": "OUT21|MC10XS4200BFK|U17"}

    in_frame_dict = {'0300': '', '0301': '', '0302': '', '0303': '', '0304': '', '0305': '',
                     '0306': '', '0307': '', '0308': '', '0309': '', '030A': '', '030B': '',
                     '030C': '', '030D': '', '0401': '', '0403': '', '0404': '', '0405': '',
                     '0406': '', '0407': '', '0408': '', '0409': '', '0500': '', '0501': '', '0502': ''}

    mio_type_dict = {0: "CeuiMIO_ePeriod", 1: "CeuiMIO_eTimeOn", 2: "CeuiMIO_eVoltage", 3: "CeuiMIO_eResistor",
                         4: "CeuiMIO_eState", 5: "CeuiMIO_eCurrentFeedback", 6: "CeuiMIO_eCurrentLEDFeedback",
                         7: "CeuiMIO_eVoltageFeedback", 8: "CeuiMIO_eTempFeedback", 9: "CeuiMIO_eNbInputType",
                         10: "CeuiMIO_eFrequency", 11: "CeuiMIO_eDutyCycle", 12: "CeuiMIO_eSensorVoltage",
                         13: "CeuiMIO_eSensorCurrent", 14: "CeuiMIO_eStatus", 15: "CeuiMIO_eDiag",
                         16: "CeuiMIO_eRetry", 17: "CeuiMIO_eTotalNbType"}


# uds交互服务
class UdsServer:
    def __init__(self, channel):
        self.channel = channel
        can.rc['interface'] = 'socketcan'
        can.rc['channel'] = self.channel
        can_bus = can.interface.Bus()
        self.tp = IsoTp(can_bus, id_source=0x0CDA01F1, id_target=0x0CDAF101, extended_id=True)
        self.cur_val = 800  # 设备电流值(单位 mA) 24V/电阻值*1000
        self.cur_scope = [self.cur_val - 100, self.cur_val + 100]

    @staticmethod
    def get_command_msg(command="%s", d_id=""):
        command_msg = command % d_id
        res_code = bytes.fromhex("6%s" % command[1:2])
        return [command_msg, res_code[0]]

    @staticmethod
    def str_to_hex(s):
        return ''.join([hex(ord(c)).replace('0x', '') for c in s]).upper()

    # send and recv uds data
    def send(self, data):
        # print("send: ", data)
        self.tp.send_pdu(bytearray.fromhex(data))

        res_data = self.tp.get_pdu()
        # print("result: ", binascii.b2a_hex(res_data))
        time.sleep(0.05)
        return res_data


class StartCheck:
    def __init__(self):
        self.uds = UdsServer("can0")

    # 此方法用于测试收集范围信息
    def test(self, set_did=None):
        if set_did is not None:
            set_did = "0%s" % str(set_did).upper()
            SendMsg.in_frame_dict = {}.copy()
            SendMsg.in_frame_dict[set_did] = ""
        for did in sorted(SendMsg.in_frame_dict):
            # 获取所有模拟量值
            for t in SendMsg.mio_type_dict.items():
                var = "%s%02X" % (did, t[0])
                get_mio_data = self.uds.get_command_msg(SendMsg.get_mio_value, var)
                get_res = self.uds.send(get_mio_data[0])
                if get_mio_data[1] == get_res[0]:
                    mio_val = struct.unpack(">I", get_res[3:7])[0]
                    name = "%s                    " % t[1]
                    print("%s    %s    %s" % (did, name[:30], mio_val))
                # else:
                #     print("fail %s %s" % (did, t[1]))
            print('------------------------------------------------------------------------')


if __name__ == "__main__":
    set_did = None
    opts, args = getopt.getopt(sys.argv[1:], "i:")
    for op, value in opts:
        if op == "-i":
            set_did = value

    StartCheck().test(set_did=set_did)

