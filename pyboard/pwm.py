# pwm.py -- put your code here!

import pyb
import micropython

# This script assumes that there is a jumper wire connecting X1 and X4

# For this example, we'll setup a timer in PWM mode to generate a servo pulse.
# Using a prescalar of 83 gives a timer-tick frequency of 1 MHz (84 MHz / 84).
# The period of 19999 gives a 20,000 usec or 20 msec period. The pulse width
# is then in microseconds.

class CPO:
    now = pyb.micros()
    count = 0


servo_pin = pyb.Pin.board.X1
t5 = pyb.Timer(2, freq=10000)
servo = t5.channel(1, pyb.Timer.PWM, pin=servo_pin)
servo.pulse_width(1000)

# debug_pin = pyb.Pin('X2', pyb.Pin.OUT_PP)

t2 = pyb.Timer(5, freq=20000)
ic_pin = pyb.Pin.board.X2
ic = t2.channel(2, pyb.Timer.IC, pin=ic_pin, polarity=pyb.Timer.RISING)

ic_start = 0
ic_width = 0


def ic_cb(tim):
    # print('------', ic_pin.value(), pyb.micros() - CPO.now)
    # CPO.now = pyb.micros()
    CPO.count += 1
    global ic_start
    global ic_width
    # debug_pin.value(1)
    # Read the GPIO pin to figure out if this was a rising or falling edge
    if ic_pin.value():
        # Rising edge - start of the pulse
        ic_start = ic.capture()
    else:
        # Fallin edge - end of the pulgse
        ic_width = ic.capture() - ic_start & 0x0fffffff
    # debug_pin.value(0)

micropython.alloc_emergency_exception_buf(100)
ic.callback(ic_cb)

while True:
    # servo.pulse_width(pw)
    CPO.count = 0
    pyb.delay(1000)
    print(CPO.count)

    # print("pulse_width = %d, ic_width = %d, ic_start = %d" % (pw, ic_width, ic_start))
    # pw = ((pw - 900) % 1100) + 1000
