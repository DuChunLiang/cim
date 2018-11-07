#!/usr/bin/env python
# -*- coding:utf-8 -*-

import pyb
from pyb import UART
from pyb import Pin
from pyb import RTC


class CPO:
    is_debug = 0
    temp_data = None
    repeat_count = 0
    max_repeat_count = 10
    power_gpio = "X17"
    close_gpio = "X18"
    run_millis = 0
    #              年  月 日 星期 时  分 秒  倒计时
    init_time = (2018, 11, 7, 3, 9, 41, 0, 0)    # 年 月 日 星期 时 分 秒 倒计时


class MonitorUart:
    def __init__(self):
        self.uart = UART(6, 115200)
        self.uart.init(baudrate=115200, bits=8, parity=None, stop=1)
        self.rtc = RTC()
        self.rtc.datetime(CPO.init_time)
        self.write_log("init uart successfully")

    def write_log(self, content=""):
        if CPO.is_debug:
            print(content)
        content = "%s, %s\r\n" % (self.get_format_time(), content)
        f = open("frame.log", "a")
        f.write(content)
        f.close()

    def get_format_time(self):
        now_time = self.rtc.datetime()
        return "%s-%s-%s %s:%s:%s" % (now_time[0], now_time[1],
                                      now_time[2], now_time[4],
                                      now_time[5], now_time[6])

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
        self.write_log("to restart")
        self.pin_low(gpio)
        pyb.delay(5000)
        self.pin_high(gpio)
        pyb.delay(15000)
        self.write_log("restart successfully")

    def get_check_sum(self, data):
        sum = 0
        for i in data:
            sum += i
        return sum & 0x00ff

    def read_data(self):
        self.write_log("start read uart")
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
                                        self.write_log("%s,%s" % ("Screen carton", str(rev)))
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
                        self.write_log("Timeout Screen carton")
                        self.restart_power(CPO.power_gpio)

            except Exception as e:
                self.write_log("Error: %s" % e)


