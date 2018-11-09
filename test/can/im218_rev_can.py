#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import time
import cantools
import can
import binascii


# 日志打印信息
def logger(content):
    now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print('%s - %s' % (now_date, content))


class CPO:
    dbc_id_list = []  # dbc信息存储 用于判断id是否存在
    multiple_list = []
    multiple_count = 0
    multiple_id_300 = []
    multiple_id_380 = []
    complete_package_300 = ""
    complete_package_380 = ""

    def __init__(self):
        pass


class Analysis:

    def __init__(self):
        pass

    def log(self, content, timestamp):
        print(content)

    # 判断id在dbc文件中是否存在
    def id_is_exist(self, _id):
        ret = True if _id in CPO.dbc_id_list else False
        return ret

    # 去掉id的地址信息
    def get_source_id(self, id):
        d = bytearray.fromhex("%04X" % id)
        d[1] = d[1] & 0xF0
        return int(binascii.b2a_hex(d), 16)

    def assembly_data(self, data):
        return [hex(c) for c in data]

    # 根据报文数据检测生成此报文的所有关联ID
    def create_multiple_id(self, multiple_id, frame_id):
        if multiple_id not in CPO.multiple_list:
            CPO.multiple_list.append(multiple_id)
        else:
            CPO.multiple_count += 1
            if CPO.multiple_count >= 3:
                if frame_id == 0x300:
                    CPO.multiple_id_300 = CPO.multiple_list.copy()
                elif frame_id == 0x380:
                    CPO.multiple_id_380 = CPO.multiple_list.copy()

                CPO.multiple_list = []
                CPO.multiple_count = 0


    # 解析can消息
    def analysis_can(self):
        logger("已启动can数据解析")

        # 加载dbc文件
        db = cantools.database.load_file('./dbc/IM218.dbc')
        # 存入dbc文件中所有id 用于判断传入id在dbc中是否存在
        for m in db.messages:
            CPO.dbc_id_list.append(m.frame_id)

        can.rc['interface'] = 'socketcan'
        can.rc['channel'] = sys.argv[1]
        can_bus = can.interface.Bus()

        while True:
            CPO.test_time = time.time()
            bo = can_bus.recv()
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

                    res = db.decode_message(frame_id, data)
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
                elif frame_id == 0x300:
                    res = db.decode_message(frame_id, data)
                    if res is not None:
                        ledi_ch_id_ex = int(res['ledi_ch_id_ex'])
                        ledi_ch_current_1 = int(res['ledi_ch%s_current' % str(ledi_ch_id_ex)])
                        ledi_ch_voltage_1 = int(res['ledi_ch%s_voltage' % str(ledi_ch_id_ex)])
                        ledi_ch_id_2 = int(res['ledi_ch%s_id' % str(ledi_ch_id_ex + 1)])
                        ledi_ch_current_2 = int(res['ledi_ch%s_current' % str(ledi_ch_id_ex + 1)])
                        ledi_ch_voltage_2 = int(res['ledi_ch%s_voltage' % str(ledi_ch_id_ex + 1)])

                        if ledi_ch_id_ex == 1:
                            CPO.complete_package_300 = ""
                            CPO.complete_package_300 += "{%s %s %s}{%s %s %s}" % (ledi_ch_id_ex,
                                                                                  ledi_ch_current_1,
                                                                                  ledi_ch_voltage_1,
                                                                                  ledi_ch_id_2,
                                                                                  ledi_ch_current_2,
                                                                                  ledi_ch_voltage_2)
                        elif ledi_ch_id_ex < 9:
                            CPO.complete_package_300 += "{%s %s %s}{%s %s %s}" % (ledi_ch_id_ex,
                                                                                  ledi_ch_current_1,
                                                                                  ledi_ch_voltage_1,
                                                                                  ledi_ch_id_2,
                                                                                  ledi_ch_current_2,
                                                                                  ledi_ch_voltage_2)
                        else:
                            CPO.complete_package_300 += "{%s %s %s}{%s %s %s}" % (ledi_ch_id_ex,
                                                                                  ledi_ch_current_1,
                                                                                  ledi_ch_voltage_1,
                                                                                  ledi_ch_id_2,
                                                                                  ledi_ch_current_2,
                                                                                  ledi_ch_voltage_2)

                            content = "0x%03X %s" % (bo.arbitration_id, CPO.complete_package_300)
                            self.log(content, bo.timestamp)

                elif frame_id == 0x380:
                    res = db.decode_message(frame_id, data)
                    if res is not None:
                        out_ch1_id = int(res['out_ch1_id'])
                        out_ch2_id = int(res['out_ch2_id'])
                        out_ch3_id = int(res['out_ch3_id'])
                        out_ch1_value = int(res['out_ch1_value'])
                        out_ch2_value = int(res['out_ch2_value'])
                        out_ch3_value = int(res['out_ch3_value'])

                        print(CPO.multiple_id_380, CPO.multiple_list, CPO.multiple_count, out_ch1_id)

                        if len(CPO.multiple_id_380) == 0:
                            self.create_multiple_id(out_ch1_id, frame_id)
                        else:
                            pack_data = ""
                            if out_ch1_id > 0:
                                pack_data += "{%s %s}" % (out_ch1_id, out_ch1_value)
                            if out_ch2_id > 0:
                                pack_data += "{%s %s}" % (out_ch2_id, out_ch2_value)
                            if out_ch3_id > 0:
                                pack_data += "{%s %s}" % (out_ch3_id, out_ch3_value)

                            if out_ch1_id == CPO.multiple_id_380[0]:
                                CPO.complete_package_380 = ""
                                CPO.complete_package_380 += pack_data
                            elif out_ch1_id != CPO.multiple_id_380[len(CPO.multiple_id_380) - 1]:
                                CPO.complete_package_380 += pack_data
                            else:
                                CPO.complete_package_380 += pack_data

                                content = "0x%03X %s" % (bo.arbitration_id, CPO.complete_package_380)
                                self.log(content, bo.timestamp)

                elif frame_id == 0x100:
                    res = db.decode_message(frame_id, data)
                    if res is not None:
                        ana1 = int(res['ana1'])
                        ana2 = int(res['ana2'])

                        content = "0x%03X ana1=%s, ana2=%s" % (bo.arbitration_id, ana1, ana2)
                        self.log(content, bo.timestamp)

                elif frame_id == 0x400:
                    res = db.decode_message(frame_id, data)
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
                    res = db.decode_message(frame_id, data)
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


if __name__ == "__main__":
    a = Analysis()
    a.analysis_can()

#2D03000000000000
#5406000000000000
#8709000000000000
#0A000000