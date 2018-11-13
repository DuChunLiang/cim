# pwm.py -- put your code here!

import pyb
from pyb import Pin, Timer  # , Switch, LED
import micropython

micropython.alloc_emergency_exception_buf(100)


class CPO:
    rate = 2  # Hz(每秒多少次变更)
    pin = "X1"
    op_time = pyb.millis()
    timer = None
    is_switch = False


class Pulse:

    def __init__(self):
        pass

    def start(self):
        print("start pulse change rate=%s" % CPO.rate)
        CPO.timer = Timer(5, freq=CPO.rate)
        channel = CPO.timer.channel(1, Timer.PWM, pin=Pin("X1"))
        channel.pulse_width_percent(50)

    def stop(self):
        if CPO.timer is not None:
            print("stop pulse change", CPO.timer)
            CPO.timer.deinit()

    def my_switch(self):
        print(CPO.is_switch)
        freq_time = pyb.millis() - CPO.op_time
        if freq_time > 1000:
            if CPO.is_switch:
                LED(2).off()
                self.stop()
            else:
                LED(2).on()
                self.start()
            CPO.op_time = pyb.millis()


def main():
    p = Pulse()
    p.start()
    # sw = Switch()
    # sw.callback(p.my_switch)


