# main.py -- put your code here!

import pyb
from pyb import Pin
from pyb import LED
from pyb import Switch
from pyb import CAN
import ustruct
import micropython
import random
# import _thread

micropython.alloc_emergency_exception_buf(100)


class Temp:
    op_time = pyb.millis()
    on_off = 0
    acc_distance_val = 0
    lane_red_left = 0
    up_or_down = 0
    up_down_count = 0

    engSpeed = 10
    isRise = 1
    speed = 0
    count = 0

    is_run = False


class Data:
    def __init__(self):
        pass


class Test:
    def __init__(self):
        self.can = CAN(1)
        self.can.init(CAN.NORMAL, extframe=True, prescaler=21, sjw=1, bs1=5, bs2=10)
        self.can.setfilter(0, CAN.MASK32, 0, (0x0, 0x0))


    def run_switch(self):
        freq_time = pyb.millis() - Temp.op_time
        if freq_time > 1000:
            if Temp.is_run:
                LED(3).off()
                Temp.is_run = False
            else:
                LED(3).on()
                Temp.is_run = True
            Temp.op_time = pyb.millis()

    def send_can(self, can_id=None, can_data=None):
        try:
            # print(pyb.millis(), can_id, '#', can_data)
            self.can.send(can_data, can_id)
            pyb.udelay(800)
        except Exception as e:
            pass

    def key_on_off(self):
        if Temp.is_run:
            switch_pin = Pin('X1', Pin.OUT_OD)
            switch_pin.low()
            pyb.delay(500)
            switch_pin.high()

    def key_down(self):
        if Temp.is_run:
            down_pin = Pin('Y6', Pin.OUT_OD)
            down_pin.low()
            pyb.delay(500)
            down_pin.high()

    def key_up(self):
        if Temp.is_run:
            up_pin = Pin('Y7', Pin.OUT_OD)
            up_pin.low()
            pyb.delay(500)
            up_pin.high()

    def key_enter(self):
        if Temp.is_run:
            enter_pin = Pin('Y8', Pin.OUT_OD)
            enter_pin.low()
            pyb.delay(500)
            enter_pin.high()

    # ACCDistance
    def ontimer_test1_100(self):
        if Temp.is_run:
            can_id = 0x10FE6F2A
            can_data = ustruct.pack('<HBB2H', 0, 0, 16, 0, 0)
            if Temp.acc_distance_val == 2:
                can_data = ustruct.pack('<4H', 0, 0, 0, 0)
                Temp.acc_distance_val = 0
            else:
                Temp.acc_distance_val = 2
            self.send_can(can_id, can_data)

            b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'

    def ontimer_10_1(self):
        if Temp.is_run:
            acc_mode_can_id = 0x10FE6F2A
            acc_mode_can_data = ustruct.pack('<HBB2H', 0, 0, 16, 0, 0)
            self.send_can(acc_mode_can_id, acc_mode_can_data)

            ldw_status_can_id = 0x18FFD0E8
            ldw_status_can_data = ustruct.pack('<BB3H', 2, 0, 0, 0, 0)
            self.send_can(ldw_status_can_id, ldw_status_can_data)

            target_detected_can_id = 0x10FE6F2A
            target_detected_can_data = ustruct.pack('<3HBB', 0, 0, 0, 1, 0)
            self.send_can(target_detected_can_id, target_detected_can_data)

    # laneRedLeft
    def ontimer_test1_50(self):
        if Temp.is_run:
            can_id = 0x10F007E8
            can_data = ustruct.pack('<BB3H', 1, 0, 0, 0, 0)
            if Temp.lane_red_left == 1:
                can_data = ustruct.pack('<4H', 0, 0, 0, 0)
                Temp.lane_red_left = 0
            else:
                Temp.lane_red_left = 1
            self.send_can(can_id, can_data)

    # CCVS_SPEED
    def ontimer_speed_50(self):
        if Temp.is_run:
            can_id = 0x18FEF127
            can_data = ustruct.pack('<B3HB', 0, int((Temp.engSpeed * 0.08)/0.003906), 0, 0, 0)
            self.send_can(can_id, can_data)

    # S_EngineSpeed
    def ontimer_eec1_5(self):
        if Temp.is_run:
            can_id = 0xCF00400
            can_data = ustruct.pack('<HB2HB', 0, 0, int(Temp.engSpeed / 0.125), 0, 0)
            if Temp.isRise:
                Temp.engSpeed += 1
                if Temp.engSpeed > 2000:
                    Temp.isRise = 0
            else:
                Temp.engSpeed -= 1
                if Temp.engSpeed <= 10:
                    Temp.isRise = 1
            self.send_can(can_id, can_data)


def key_thread():
    t = Test()
    # sw = Switch()
    # sw.callback(t.run_switch)
    while True:
        pyb.delay(1)
        Temp.count += 1
        if Temp.count % random.randint(500, 2000) == 0:
            t.key_on_off()
            if Temp.up_down_count > 3:
                Temp.up_down_count = 0
                if Temp.up_or_down:
                    Temp.up_or_down = 0
                else:
                    Temp.up_or_down = 1

        if Temp.count % random.randint(500, 2000) == 0:
            Temp.up_down_count += 1
            if Temp.up_or_down:
                t.key_up()
            else:
                t.key_down()

        if Temp.count % random.randint(500, 2000) == 0:
            t.key_enter()


def can_thread():
    t = Test()
    sw = Switch()
    sw.callback(t.run_switch)
    while True:
        pyb.delay(1)
        Temp.count += 1

        if Temp.count % 10 == 0:
            t.ontimer_10_1()

        if Temp.count % 100 == 0:
            t.ontimer_test1_100()

        if Temp.count % 60 == 0:
            t.ontimer_test1_50()

        if Temp.count % 50 == 0:
            t.ontimer_speed_50()

        if Temp.count % 5 == 0:
            t.ontimer_eec1_5()


# def main():
#     t = Test()
#     sw = Switch()
#     sw.callback(t.run_switch)
#
#     _thread.start_new_thread(key_thread, ())
#     _thread.start_new_thread(can_thread, ())

