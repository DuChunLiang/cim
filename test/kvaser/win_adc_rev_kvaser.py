#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import binascii
import time
import tkinter as tk
import threading
from canlib import canlib, kvadblib


# 日志打印信息
def logger(content):
    now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print('%s - %s' % (now_date, content))


class CPO:
    def __init__(self):
        pass

    run_function = None
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


class CanShow:

    def __init__(self, wigth=800, higth=500):
        self.dbc_file = "../../dbc/adc_lc.dbc"
        self.root = tk.Tk(className='Can Info Show')
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw-wigth) / 2
        y = (sh-higth) / 2
        self.root.geometry("%dx%d+%d+%d" % (wigth, higth, x, y))

        self.var_1 = tk.StringVar()
        self.var_2 = tk.StringVar()
        self.var_3 = tk.StringVar()
        self.var_4 = tk.StringVar()
        self.var_5 = tk.StringVar()

        self.add_label()
        self.add_button()

    @staticmethod
    def thread_run():
        if CPO.run_function is not None:
            t = threading.Thread(target=CPO.run_function)
            t.setDaemon(True)
            t.start()
        else:
            raise Exception("variable 'run_function' is None, please set 'CPO.run_function'")

    def add_label(self):
        label_1 = tk.Label(self.root, textvariable=self.var_1)
        # label_2 = tk.Label(self.root, text='d45s6f4a56sd4f56sa4df56sa4df564sadf')
        # label_3 = tk.Label(root, text='d45s6f4a56sd4f56sa4df56sa4df564sadf')
        # label_4 = tk.Label(root, text='d45s6f4a56sd4f56sa4df56sa4df564sadf')
        # label_5 = tk.Label(root, text='d45s6f4a56sd4f56sa4df56sa4df564sadf')
        label_1.place(x=30, y=20, anchor="w")
        # label_2.place(x=30, y=50, anchor="w")
        # label_3.pack()
        # label_4.pack()
        # label_5.pack()

    def add_button(self):
        CPO.run_function = self.rev_data
        button = tk.Button(self.root, text='start', width=15,
                           height=1, command=self.thread_run)
        button.pack(side=tk.BOTTOM)

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
            self.analysis_can(msg.id, msg.name, self.get_signal_dict(bmsg))
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

    @staticmethod
    def assembly_data(data):
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
                    self.var_1.set(content)


CanShow().run()
