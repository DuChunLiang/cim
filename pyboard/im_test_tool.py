#!/usr/bin/env python
# -*- coding:utf-8 -*-

import pyb
from pyboard import im_config
from pyb import UART
from pyb import Pin
from pyb import RTC


class ImTest:

    def __init__(self):
        pass

    def pin_off(self, gpio):
        pin = Pin(gpio, Pin.OUT_PP)
        while pin.value() == 1:
            # print("low")
            pin.low()

    def pin_on(self, gpio):
        pin = Pin(gpio, Pin.OUT_PP)
        while pin.value() == 0:
            # print("high")
            pin.high()

