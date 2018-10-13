from pyb import UART
from pyb import Pin
from micropyGPS import MicropyGPS
# Global Flag to Start GPS data Processing
print('GPS Interrupt Tester')

# Instantiate the micropyGPS object
my_gps = MicropyGPS()
# Setup the connection to your GPS here
# This example uses UART 3 with RX on pin Y10
# Baudrate is 9600bps, with the standard 8 bits, 1 stop bit, no parity
# Also made the buffer size very large (1000 chars) to accommodate all the characters that stack up
# each second
uart = UART(6, 9600, read_buf_len=1000)

# Create an external interrupt on pin X8
def Read_GPS():
        while uart.any():
            my_gps.update(chr(uart.readchar()))  # Note the conversion to to chr, UART outputs ints normally
        
        print('UTC Timestamp:', my_gps.timestamp)
        print('Date:', my_gps.date_string('long'))
        print('Latitude:', my_gps.latitude_string())
        print('Longitude:', my_gps.longitude_string())
        print('Horizontal Dilution of Precision:', my_gps.hdop)
        print()
        new_data = False  # Clear the flag
