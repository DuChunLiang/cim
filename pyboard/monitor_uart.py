#!/usr/bin/env python
# -*- coding:utf-8 -*-

import pyb
from pyb import UART


class CPO:
    temp_data = None
    repeat_count = 0
    max_repeat_count = 10


class MonitorUart:

    def __init__(self):
        self.uart = UART(6, 115200)
        self.uart.init(baudrate=115200, bits=8, parity=None, stop=1)
        print("init uart successfully")

    def reset_uart(self):
        self.uart.deinit()
        self.uart = UART(6, 115200)
        self.uart.init(baudrate=115200, bits=8, parity=None, stop=1)
        print("reset uart successfully")
        pyb.delay(5000)

    def get_check_sum(self, data):
        sum = 0
        for i in data:
            sum += i
        return sum & 0x00ff

    def read_data(self):
        print("start read uart")
        # clear log info
        f = open("frame.log", "a")
        f.write("2018-11-05 16:21\r\n")
        f.close()

        while True:
            try:
                # pyb.delay(100)
                if self.uart.any() > 0:
                    rev = self.uart.readline()
                    # print(rev, len(rev))
                    if len(rev) == 15:
                        # head = rev[12:]
                        # checkout_bit = head[0]
                        # type = head[1]
                        # data_len = head[2]
                        data = rev[:10]
                        check_sum = rev[10]

                        # print('---', data, self.get_check_sum(data), check_sum)
                        if self.get_check_sum(data) == check_sum:

                            if CPO.temp_data is not None:
                                if CPO.temp_data == check_sum:
                                    CPO.repeat_count += 1
                                    if CPO.repeat_count >= CPO.max_repeat_count:
                                        f = open("frame.log", "a")
                                        f.write("%s, %s, %s\r\n" % (pyb.millis()/1000, "Screen carton", str(rev)))
                                        f.close()
                                else:
                                    CPO.repeat_count = 0

                            # print(pyb.millis(), rev, check_sum, len(rev), CPO.repeat_count)
                            CPO.temp_data = check_sum
                        # else:
                            # f = open("frame.log", "a")
                            # f.write("%s, %s, %s\r\n" % (pyb.millis()/1000, "Error Frame", str(rev)))
                            # f.close()
                            # print(rev, self.get_check_sum(data), check_sum, "Error Frame, reset uart")
            except Exception as e:
                print('Error:', e)


