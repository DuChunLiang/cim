#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import binascii
import time
import threading
# import struct
import random
from canlib import canlib, kvadblib, Frame

if sys.version_info.major == 2:
    import Tkinter as tk
else:
    import tkinter as tk


# 日志打印信息
def logger(content):
    now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print('%s - %s' % (now_date, content))


class CPO:
    def __init__(self):
        pass

    multiple_list = []
    multiple_count = 0
    multiple_id_300 = []
    multiple_id_380 = []
    complete_package_300 = ""
    complete_package_380 = ""
    receive_is_run = False
    receive_thread_run = False
    send_is_run = False
    send_thread_run = False
    run_function = None
    dbc_id_list = []  # dbc信息存储 用于判断id是否存在

    bitrates = {
        '1M': canlib.canBITRATE_1M,
        '500K': canlib.canBITRATE_500K,
        '250K': canlib.canBITRATE_250K,
        '125K': canlib.canBITRATE_125K,
        '100K': canlib.canBITRATE_100K,
        '62K': canlib.canBITRATE_62K,
        '50K': canlib.canBITRATE_50K,
        '83K': canlib.canBITRATE_83K,
        '10K': canlib.canBITRATE_10K,
    }


class CanShow:

    def __init__(self, wigth=800, higth=500):
        self.dbc_file = "../../dbc/IM218.dbc"
        self.root = tk.Tk()
        self.root.title('Can Show Tool')
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - wigth) / 2
        y = (sh - higth) / 2
        self.root.geometry("%dx%d+%d+%d" % (wigth, higth, x, y))

        self.label_1 = tk.Label(self.root, text="0x200")
        self.label_2 = tk.Label(self.root, text="0x280")
        self.label_3 = tk.Label(self.root, text="0x300")
        self.label_4 = tk.Label(self.root, text="0x380")
        self.label_5 = tk.Label(self.root, text="0x100")
        self.label_6 = tk.Label(self.root, text="0x400")
        self.label_7 = tk.Label(self.root, text="0x080", wraplength=500, justify='left')

        self.add_label()
        self.add_button()

    def receive_thread_run(self):
        if not CPO.receive_thread_run:
            if not CPO.receive_is_run:
                my_thread = threading.Thread(target=self.rev_data)
                my_thread.setDaemon(True)
                my_thread.start()
                CPO.receive_is_run = True
            CPO.receive_thread_run = True
            receive_button['text'] = "接收:stop"
            receive_button['bg'] = "green"
            logger("接收:start")
        else:
            CPO.receive_thread_run = False
            receive_button['text'] = "接收:start"
            receive_button['bg'] = "#DD4822"
            logger("接收:stop")

    def send_thread_run(self):
        if not CPO.send_thread_run:
            if not CPO.send_is_run:
                my_thread = threading.Thread(target=self.send_data)
                my_thread.setDaemon(True)
                my_thread.start()
                CPO.send_is_run = True
            CPO.send_thread_run = True
            send_button['text'] = "发送:stop"
            send_button['bg'] = "green"
            logger("发送:start")
        else:
            CPO.send_thread_run = False
            send_button['text'] = "发送:start"
            send_button['bg'] = "#DD4822"
            logger("发送:stop")

    def add_label(self):
        self.label_1.place(x=30, y=20, anchor="nw")
        self.label_2.place(x=30, y=50, anchor="nw")
        self.label_3.place(x=30, y=80, anchor="nw")
        self.label_4.place(x=30, y=110, anchor="nw")
        self.label_5.place(x=30, y=140, anchor="nw")
        self.label_6.place(x=30, y=170, anchor="nw")
        self.label_7.place(x=30, y=200, anchor="nw")

    def add_button(self):
        global receive_button
        # CPO.run_function = self.rev_data
        receive_button = tk.Button(self.root, text="接收:start", width=15,
                                   height=1, command=self.receive_thread_run, bg="#DD4822", fg="white")
        receive_button.place(x=300, y=480, anchor="s")

        global send_button
        # CPO.run_function = self.send_data
        send_button = tk.Button(self.root, text="发送:start", width=15,
                                height=1, command=self.send_thread_run, bg="#DD4822", fg="white")
        send_button.place(x=500, y=480, anchor="s")

    def run(self):
        self.root.mainloop()

    # --------------------------------kvaser can------------------------------
    @staticmethod
    def _set_up_channel(channel=0, open_flags=canlib.Open.ACCEPT_VIRTUAL,
                        bitrate='250K', output_control=canlib.Driver.NORMAL):
        ch = canlib.openChannel(channel, open_flags)
        ch.setBusOutputControl(output_control)
        ch.setBusParams(CPO.bitrates[bitrate])
        ch.busOn()
        return ch

    @staticmethod
    def _tear_down_channel(ch):
        ch.busOff()
        ch.close()

    def rev_data(self):
        logger("Listening...")
        db = kvadblib.Dbc(filename=self.dbc_file)
        ch = self._set_up_channel()
        for m in db.messages():
            CPO.dbc_id_list.append(m.id)

        while True:
            try:
                frame = ch.read(5 * 60 * 1000)
                frame.data = (frame.data + bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0]))[:8]
                if CPO.receive_thread_run and self.id_is_exist(self.get_source_id(frame.id)):
                    self._op_frame(frame, db)
            except Exception as e:
                self._tear_down_channel(ch)
                print(e)

    def send_data(self):
        logger("send can...")
        ch = self._set_up_channel()
        csd = CreateSendData()
        state = 0
        record_time = 0
        # now_time = time.time()
        while True:
            try:
                if CPO.send_thread_run:
                    if record_time % 40 == 0:
                        if state:
                            state = 0
                        else:
                            state = 1

                    frame_id = 0x0C1
                    frame = Frame(id_=frame_id, data=csd.get_data(frame_id=frame_id, state=1))
                    ch.write(frame)
                    # print(hex(frame.id), frame.data)

                    for i in range(1, 4):
                        frame_id = 0x141
                        frame = Frame(id_=frame_id, data=csd.get_data(frame_id=frame_id,
                                                                      state=state, pack_num=i))
                        ch.write(frame)
                        # print(hex(frame.id), frame.data)
                        time.sleep(0.01)

                    frame_id = 0x1C1
                    frame = Frame(id_=frame_id, data=csd.get_data(frame_id=frame_id, state=state))
                    ch.write(frame)
                    # print(hex(frame.id), frame.data)

                    time.sleep(0.04)
                    record_time += 5
                    # print('----', (time.time()-now_time)*1000)
                    # now_time = time.time()
            except Exception as e:
                # self._tear_down_channel(ch)
                print(e)

    @staticmethod
    def get_signal_dict(bmsg):
        signal_dict = {}
        for bsig in bmsg:
            signal_dict[bsig.name] = bsig.value
        return signal_dict

    def _op_frame(self, frame, db):
        try:
            show_frame_id = frame.id
            frame.id = self.get_source_id(frame.id)
            bmsg = db.interpret(frame)
            msg = bmsg._message
            data_len = frame.dlc

            self.analysis_can(msg.id, show_frame_id, msg.name, self.get_signal_dict(bmsg), data_len)
        except kvadblib.KvdNoMessage:
            print("<<< No message found for frame with id %s >>>" % frame.id)

    # --------------------------------dbc can------------------------------
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
    def analysis_can(self, frame_id, show_frame_id, message_name, res, data_len):
        if len(sys.argv) >= 2:
            if int(sys.argv[1], 16) != frame_id:
                frame_id = 0x100000000

        if frame_id == 0x200 or frame_id == 0x280:
            ifreq_index = 1
            if frame_id == 0x280:
                ifreq_index = 2

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
                content = "0x%03X ton=%s, toff=%s" % (show_frame_id, str(ton), str(toff))
                logger(content)
                if ifreq_index == 1:
                    self.label_1['text'] = content
                else:
                    self.label_2['text'] = content
        elif frame_id == 0x300:
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

                    content = "0x%03X %s" % (show_frame_id, CPO.complete_package_300)
                    logger(content)
                    self.label_3['text'] = content

        elif frame_id == 0x380:
            if res is not None:
                if res is not None:
                    out_ch1_id = int(res['out_ch1_id'])
                    out_ch2_id = int(res['out_ch2_id'])
                    out_ch3_id = int(res['out_ch3_id'])
                    out_ch1_value = int(res['out_ch1_value'])
                    out_ch2_value = int(res['out_ch2_value'])
                    out_ch3_value = int(res['out_ch3_value'])

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

                            content = "0x%03X %s" % (show_frame_id, CPO.complete_package_380)
                            logger(content)
                            self.label_4['text'] = content
        elif frame_id == 0x100:
            if res is not None:
                ana1 = int(res['ana1'])
                ana2 = int(res['ana2'])

                content = "0x%03X ana1=%s, ana2=%s" % (show_frame_id, ana1, ana2)
                logger(content)
                self.label_5['text'] = content
        elif frame_id == 0x400:
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
                          "sens1_inf=%s" % (show_frame_id, sens1_inf, sens2_inf, wiper_Fail,
                                            oilavl, Vbat_inf, V1_inf, V2_inf)

                logger(content)
                self.label_6['text'] = content
        elif frame_id == 0x80:
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
                          "uin7_bool=%s, uin7_inf=%s" % (show_frame_id, res['wk1_state'],
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
                logger(content)
                self.label_7['text'] = content


# 转换
class Convert:
    def __init__(self):
        self.hexmap = {
            "0000": "0",
            "0001": "1",
            "0010": "2",
            "0011": "3",
            "0100": "4",
            "0101": "5",
            "0110": "6",
            "0111": "7",
            "1000": "8",
            "1001": "9",
            "1010": "A",
            "1011": "B",
            "1100": "C",
            "1101": "D",
            "1110": "E",
            "1111": "F",
        }

    def addone(self, mods):
        assert isinstance(mods, list)
        tmods = mods.copy()
        if tmods:
            if tmods[0] == 0:
                tmods[0] = 1
                return (tmods)
            else:
                return ([0] + self.addone(tmods[1:]))
        return ([])

    def convertToBinary(self, num, site=64):
        assert -2 ** (site - 1) <= num < 2 ** (site - 1), "the %d is not in range [%d,%d)" % (
            num, -2 ** (site - 1), 2 ** (site - 1))
        mod = []
        quotient = abs(num)
        if quotient == 0:
            mod = [0]
        else:
            while quotient:
                mod.append(quotient % 2)
                quotient = quotient // 2
        mod += [0] * (site - len(mod) - 1)
        # if negative
        if num < 0:
            # not
            mod = [0 if i else 1 for i in mod]
            # add 1
            mod = self.addone(mod)
            # add sign
            mod += [1]
        else:
            mod += [0]
        return ("".join([str(i) for i in reversed(mod)]))

    def convertToHex(self, code):
        clen = len(code)
        mod = clen % 4
        if mod != 0:
            if code[0] == 0:
                code = "0" * (4 - mod) + code
            else:
                code = "1" * (4 - mod) + code
        out = []
        for i in range(0, len(code), 4):
            out.append(self.hexmap[code[i:i + 4]])
        return ("".join(out))


# 创建发送数据类
class CreateSendData:
    def __init__(self, ):
        pass

    def get_random(self, s=0, e=9, length=1):
        res_random = ""
        for i in range(length):
            res_random += str(random.randint(s, e))
        return res_random

    @staticmethod
    def get_data(frame_id=0x0, state=0, pack_num=1):
        can_data = bytearray()
        if frame_id == 0x0C1:
            if state == 0:
                can_data = bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00")
            else:
                can_data = bytearray(b"\x55\x64\x64\x64\x64\xFF\xFF\x00")
        elif frame_id == 0x141:
            if state == 0:
                if pack_num == 1:
                    can_data = bytearray(b"\x10\x32\x54\x00\x00\x00\x00\x00")
                elif pack_num == 2:
                    can_data = bytearray(b"\x65\x87\x59\x00\x00\x00\x00\x00")
                elif pack_num == 3:
                    can_data = bytearray(b"\xBA\xDC\x5E\x00\x00\x00\x00\x00")
            else:
                if pack_num == 1:
                    can_data = bytearray(b"\x10\x32\x54\x64\x64\x64\x64\x64")
                elif pack_num == 2:
                    can_data = bytearray(b"\x65\x87\x59\x64\x64\x64\x64\x64")
                elif pack_num == 3:
                    can_data = bytearray(b"\xBA\xDC\x5E\x64\x64\x64\x64\x64")
        elif frame_id == 0x1C1:
            if state == 0:
                can_data = bytearray(b"\x00\x00\x00\x28\x00\x00\x00\x00")
            else:
                can_data = bytearray(b"\x00\x00\x00\x28\x00\x00\x00\x00")
        return can_data


CanShow().run()

# a = CreateSendData(0x0C0).get_data()
# print(a)
