# main.py -- put your code here!

import mycan
import monitor_uart_218
import _thread

# _thread.start_new_thread(monitor_uart.MonitorUart().monitor_card_screen, ())
_thread.start_new_thread(monitor_uart_218.MonitorUart().monitor_restart, ())
# _thread.start_new_thread(mycan.key_thread, ())
# _thread.start_new_thread(mycan.can_thread, ())
