#!/usr/bin/env python

# import sys
# import getopt
import os
import can
import time
import struct
# import binascii
from udstools import IsoTp


# 日志
def logger(content, is_file=False, path="./logs/error.log"):
    now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    log_data = '%s - %s\r\n' % (now_date, content)
    print(log_data)
    if is_file:
        if not os.path.exists("./logs/"):
            os.makedirs("./logs/")

        log_file = open(path, "a")
        log_file.write(log_data)
        log_file.close()


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

    output_flag = "2F"  # 输出标志位
    in_flag = "22"  # 输入标志位

    frame_dict = {"0100": "OUT1|MC06XS4200BFK|U4", "0101": "OUT2|MC06XS4200BFK|U4",
                  "0102": "OUT3|MC10XS4200BFK|U6", "0103": "OUT4|MC10XS4200BFK|U6",
                  "0104": "OUT5|MC10XS4200BFK|U9", "0105": "OUT6|MC10XS4200BFK|U9",
                  "0106": "OUT7|MC10XS4200BFK|U5", "0107": "OUT8|MC10XS4200BFK|U5",
                  "0108": "OUT9|MC10XS4200BFK|U8", "0109": "OUT10|MC10XS4200BFK|U8",
                  "010A": "OUT11|MC10XS4200BFK|U7", "010B": "OUT12|MC10XS4200BFK|U7",
                  "010C": "OUT13|MC10XS4200BFK|U15", "010D": "OUT14|MC10XS4200BFK|U15",
                  "010E": "OUT15|MC10XS4200BFK|U16", "010F": "OUT16|MC10XS4200BFK|U16",
                  "0110": "OUT17|MC10XS4200BFK|U18", "0111": "OUT18|MC10XS4200BFK|U18",
                  "0112": "OUT19|MC10XS4200BFK|U19", "0113": "OUT20|MC10XS4200BFK|U19",
                  "0201": "OUT21|MC10XS4200BFK|U17"}

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
        self.tp = IsoTp(can_bus, id_source=0x0CDA05F1, id_target=0x0CDAF105, extended_id=True)
        self.cur_val = 800    # 设备电流值(单位 mA) 24V/电阻值*1000
        self.cur_scope = [self.cur_val-100, self.cur_val+100]

    # 组装输出报文
    @staticmethod
    def pack_out_uds_msg(did="0100", command="03", d1="00", d2="00"):
        command_msg = "%s%s%s%s%s" % (SendMsg.output_flag, did, command, d1, d2)
        res_code = bytes.fromhex("6%s" % SendMsg.output_flag[1:2])
        return [command_msg, res_code[0]]

    # 组装输入报文
    @staticmethod
    def pack_in_uds_msg(did="0100", data_type="00"):
        command_msg = "%s%s%s" % (SendMsg.in_flag, did, data_type)
        res_code = bytes.fromhex("6%s" % SendMsg.in_flag[1:2])
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

    # 检查
    def check(self, did, ran, remark):
        d1 = "00"
        data_type = "06"
        if did == "0201":
            d1 = "0C"
            data_type = "07"

        out_set_data = self.uds.pack_out_uds_msg(did=did, command="03", d1=d1, d2=ran)
        # 输出模拟量
        set_res = self.uds.send(out_set_data[0])
        if out_set_data[1] == set_res[0]:
            get_mio_data = self.uds.pack_in_uds_msg(did=did, data_type=data_type)
            get_res = self.uds.send(get_mio_data[0])
            if get_mio_data[1] == get_res[0]:
                mio_val = struct.unpack(">I", get_res[3:7])[0]
                time.sleep(0.5)
                if did == "0201":
                    correct_val = int(ran, 16) * 60
                    correct_scope = [correct_val - 1000, correct_val + 1000]
                    content = "%s %s %s[%s %s]" % (did, remark, mio_val, correct_scope[0], correct_scope[1])
                    if mio_val < correct_scope[0] or mio_val > correct_scope[1]:
                        logger(content=content, is_file=True)
                    else:
                        logger(content=content)
                else:
                    content = "%s %s %s[%s %s]" % (did, remark, mio_val,
                                                   self.uds.cur_scope[0], self.uds.cur_scope[1])
                    if mio_val < self.uds.cur_scope[0] or mio_val > self.uds.cur_scope[1]:
                        logger(content=content, is_file=True)
                    else:
                        logger(content=content)
            else:
                print("fail %s CeuiMIO_eCurrentLEDFeedback" % did)
        else:
            print("%s out fail" % did)

        # 关闭输出模拟量
        out_set_data = self.uds.pack_out_uds_msg(did=did, command="03", d1=d1, d2="00")
        self.uds.send(out_set_data[0])
        time.sleep(1)
        data_type = "05"
        if did == "0201":
            data_type = "07"

        get_mio_data = self.uds.pack_in_uds_msg(did=did, data_type=data_type)
        get_res = self.uds.send(get_mio_data[0])
        if get_mio_data[1] == get_res[0]:
            mio_val = struct.unpack(">I", get_res[3:7])[0]
            content = "%s %s %s[0 0]" % (did, remark, mio_val)
            if mio_val > 0:
                logger(content=content, is_file=True)
            else:
                logger(content=content)

    # 此方法用于正式测试
    def start(self):
        while True:
            for frame in sorted(SendMsg.frame_dict):
                did = frame
                remark = ("%s          " % SendMsg.frame_dict[frame])[:30]

                if did == "0201":
                    for ran in ["0A", "C8", "FA"]:
                        self.check(did, ran, remark)
                else:
                    ran = "64"
                    self.check(did, ran, remark)
            time.sleep(2)


if __name__ == "__main__":
    # set_did = None
    # set_ran = None
    # opts, args = getopt.getopt(sys.argv[1:], "i:r:")
    # for op, value in opts:
    #     if op == "-i":
    #         set_did = value
    #     elif op == "-r":
    #         set_ran = value
    #
    # StartCheck().test(set_did=set_did, set_ran=set_ran)

    StartCheck().start()
