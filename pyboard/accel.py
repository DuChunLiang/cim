import pyb
from pyb import Accel
from pyb import LED
accel = pyb.Accel()
before_x = 0
led = LED(1)
def Read_ACCEL():
	global before_x
	x = accel.x()
	y = accel.y()
	z = accel.z()
	if -3<before_x-x<3:
		#print('ok')
		before_x = x
		led.off()
		return 0
	else:
		print(x,y,z)
		before_x = x
		led.on()
		return 1