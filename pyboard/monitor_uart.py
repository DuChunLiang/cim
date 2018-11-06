#!/usr/bin/env python
# -*- coding:utf-8 -*-

import pyb
from pyb import UART
from pyb import Pin


class CPO:
    temp_data = None
    repeat_count = 0
    max_repeat_count = 10
    power_gpio = "X17"
    close_gpio = "X18"
    run_millis = 0


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

    def pin_low(self, gpio):
        pin = Pin(gpio, Pin.OUT_PP)
        while pin.value() == 1:
            # print("low")
            pin.low()

    def pin_high(self, gpio):
        pin = Pin(gpio, Pin.OUT_PP)
        while pin.value() == 0:
            # print("high")
            pin.high()

    def restart_power(self, gpio):
        f = open("frame.log", "a")
        f.write("%s, %s\r\n" % (pyb.millis()/1000, "to restart"))
        # print("to restart")
        self.pin_low(gpio)
        pyb.delay(5000)
        self.pin_high(gpio)
        f.write("%s, %s\r\n" % (pyb.millis()/1000, "restart successfully"))
        # print("restart successfully")
        f.close()
        pyb.delay(10000)

    def get_check_sum(self, data):
        sum = 0
        for i in data:
            sum += i
        return sum & 0x00ff

    def read_data(self):
        print("start read uart")
        f = open("frame.log", "a")
        f.write("2018-11-06 17:56\r\n")
        f.close()

        while True:
            try:
                self.pin_low(CPO.close_gpio)
                self.pin_high(CPO.power_gpio)
                if self.uart.any() > 0:
                    CPO.run_millis = pyb.millis()
                    rev = self.uart.readline()
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

                                        self.restart_power(CPO.power_gpio)
                                else:
                                    CPO.repeat_count = 0

                            # print(pyb.millis(), rev, self.get_check_sum(data), check_sum)
                            CPO.temp_data = check_sum
                        # else:
                            # f = open("frame.log", "a")
                            # f.write("%s, %s, %s\r\n" % (pyb.millis()/1000, "Error Frame", str(rev)))
                            # f.close()
                            # print(rev, self.get_check_sum(data), check_sum, "Error Frame, reset uart")
                else:
                    if (pyb.millis() - CPO.run_millis) > 10*1000:
                        f = open("frame.log", "a")
                        f.write("%s, %s, %s\r\n" % (pyb.millis()/1000, "Timeout Screen carton", str(rev)))
                        f.close()
                        self.restart_power(CPO.power_gpio)
                        # print("Timeout Screen carton")

            except Exception as e:
                print('Error:', e)


