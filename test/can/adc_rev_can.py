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
    msg_signal_dict = {0x401: ['14', '13'], 0x402: ['01', '02'], 0x403: ['04', '03'],
                       0x404: ['08', '07'], 0x405: ['20', '19'], 0x406: ['16', '15'],
                       0x407: ['09', '10'], 0x408: ['12', '11'], 0x409: ['18', '17'],
                       0x410: ['06', '05'], }

    def __init__(self):
        print('')


class Analysis:

    def __init__(self):
        pass

    def log(self, content):
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

    # 根据adc值计算电流
    def get_current(self, adc_val, frame_id):
        if frame_id == 0x401 or frame_id == 0x403 \
                or frame_id == 0x407 or frame_id == 0x408 \
                or frame_id == 0x409:
            current = round((1.96/276)*adc_val, 3)
        elif frame_id == 0x402 or frame_id == 0x405:
            current = round((1.94/79)*adc_val, 3)
        else:
            current = round((1.94/131)*adc_val, 3)
        return "%sA" % str(current)

    # 解析can消息
    def analysis_can(self):
        logger("已启动can数据解析")

        # 加载dbc文件
        db = cantools.database.load_file('dbc/adc_lc.dbc')
        # 存入dbc文件中所有id 用于判断传入id在dbc中是否存在
        for m in db.messages:
            CPO.dbc_id_list.append(m.frame_id)

        can.rc['interface'] = 'socketcan'
        can.rc['channel'] = sys.argv[1]
        can_bus = can.interface.Bus()

        while True:
            bo = can_bus.recv()
            frame_id = bo.arbitration_id
            data = (bo.data + bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0]))[:8]

            if len(sys.argv) >= 3:
                if int(sys.argv[2], 16) != bo.arbitration_id:
                    frame_id = 0x100000000

            # 判断id是否存在
            if self.id_is_exist(frame_id):
                if frame_id in CPO.msg_signal_dict:
                    signal_list = CPO.msg_signal_dict[frame_id]
                    res = db.decode_message(frame_id, data)
                    if res is not None:
                        message = db.get_message_by_frame_id(frame_id)

                        signal_1 = 'OUT%s' % signal_list[0]
                        signal_2 = 'OUT%s' % signal_list[1]

                        OUT_1 = int(res[signal_1])
                        OUT_2 = int(res[signal_2])

                        content = "%s_%s %s={%s, %s}, %s={%s, %s}" % (str(message.name), hex(bo.arbitration_id),
                                                                      signal_1, str(OUT_1),
                                                                      self.get_current(OUT_1, frame_id),
                                                                      signal_2, str(OUT_2),
                                                                      self.get_current(OUT_2, frame_id))
                        self.log(content)

            # else:
            #     print('-------%s在dbc文件中不存在-------' % frame_id)


if __name__ == "__main__":
    Analysis().analysis_can()
