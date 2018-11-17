#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
# import time
import binascii
from canlib import canlib, kvadblib


# 日志打印信息
def logger(content):
    # now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    # print('%s - %s' % (now_date, content))
    print(content)


class CPO:
    dbc_id_list = []  # dbc信息存储 用于判断id是否存在
    msg_signal_dict = {0x401: ['14', '13'], 0x402: ['01', '02'], 0x403: ['04', '03'],
                       0x404: ['08', '07'], 0x405: ['20', '19'], 0x406: ['16', '15'],
                       0x407: ['09', '10'], 0x408: ['12', '11'], 0x409: ['18', '17'],
                       0x410: ['06', '05'], }

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

    def __init__(self):
        pass


class KvaserCan:
    def __init__(self):
        self.dbc_file = "../../dbc/adc_lc.dbc"

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
        print("Listening...")
        db = kvadblib.Dbc(filename=self.dbc_file)
        ch = self._set_up_channel()
        for m in db.messages():
            CPO.dbc_id_list.append(m.id)

        while True:
            try:
                frame = ch.read(5 * 60 * 1000)
                frame.data = (frame.data + bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0]))[:8]
                self._op_frame(frame, db)
            except Exception as e:
                self._tear_down_channel(ch)
                print(e)

    def get_signal_dict(self, bmsg):
        signal_dict = {}
        for bsig in bmsg:
            signal_dict[bsig.name] = bsig.value
        return signal_dict

    def _op_frame(self, frame, db):
        try:
            bmsg = db.interpret(frame)
            msg = bmsg._message
            Analysis().analysis_can(msg.id, msg.name, self.get_signal_dict(bmsg))
        except kvadblib.KvdNoMessage:
            print("<<< No message found for frame with id %s >>>" % frame.id)


class Analysis:
    def __init__(self):
        pass

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

    # 根据adc值计算电流
    def get_current(self, adc_val, frame_id):
        if frame_id == 0x401 or frame_id == 0x403 \
                or frame_id == 0x407 or frame_id == 0x408 \
                or frame_id == 0x409:
            current = round((1.96 / 276) * adc_val, 3)
        elif frame_id == 0x402 or frame_id == 0x405:
            current = round((1.94 / 79) * adc_val, 3)
        else:
            current = round((1.94 / 131) * adc_val, 3)
        return "%sA" % str(current)

    # 解析can消息
    def analysis_can(self, frame_id, message_name, signal_dict):
        if len(sys.argv) >= 2:
            if int(sys.argv[1], 16) != frame_id:
                frame_id = 0x100000000

        # 判断id是否存在
        if self.id_is_exist(frame_id):
            if frame_id in CPO.msg_signal_dict:
                signal_list = CPO.msg_signal_dict[frame_id]
                if signal_dict is not None:
                    signal_1 = 'OUT%s' % signal_list[0]
                    signal_2 = 'OUT%s' % signal_list[1]

                    OUT_1 = int(signal_dict[signal_1])
                    OUT_2 = int(signal_dict[signal_2])

                    content = "%s_%s %s={%s, %s}, %s={%s, %s}" % (message_name, hex(frame_id),
                                                                  signal_1, str(OUT_1),
                                                                  self.get_current(OUT_1, frame_id),
                                                                  signal_2, str(OUT_2),
                                                                  self.get_current(OUT_2, frame_id))
                    logger(content)


if __name__ == '__main__':
    kc = KvaserCan()
    kc.rev_data()
