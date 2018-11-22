#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import time
import subprocess
if sys.version_info.major == 2:
    import Tkinter as tk
    import Tkinter.messagebox as tmb
else:
    import tkinter as tk
    import tkinter.messagebox as tmb

log_path = r"D:\lrzsz\boot.log"


# 日志打印信息
def logger(content):
    now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    content = '%s - %s' % (now_date, content)
    print(content)
    log_f = open(log_path, "a")
    log_f.write(content)
    log_f.close()


class BootRecord:

    def __init__(self, wigth=600, higth=580):
        # self.exe_path = "../exe/error.exe"
        # self.exe_path = "../exe/success.exe"
        self.serial_code = ""

        self.list_index = 0
        self.success_count = 0
        self.error_count = 0

        self.root = tk.Tk()
        self.root.title('Boot Run Tool')
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw-wigth) / 2
        y = (sh-higth) / 2
        self.root.geometry("%dx%d+%d+%d" % (wigth, higth, x, y))

        self.serial_var = tk.StringVar()
        self.scrollbar = tk.Scrollbar(self.root)
        self.label_serial_code = tk.Label(self.root, text='Serial Code:')
        self.label_success_name = tk.Label(self.root, text='Success Count:')
        self.label_error_name = tk.Label(self.root, text='Error Count:')
        self.label_success_val = tk.Label(self.root, text='0')
        self.label_error_val = tk.Label(self.root, text='0')

        self.label_time = tk.Label(self.root, text='Time:')
        self.label_time_value = tk.Label(self.root, text='2018-01-03')
        self.boot_list = tk.Listbox(self.root, width=50)

        self.control_option()

    def control_option(self):
        anchor = "ne"

        self.root.focus()
        self.root.bind("<Key>", self.entry_key)

        self.label_time.place(x=150, y=30, anchor=anchor)
        self.label_time_value.place(x=230, y=31, anchor=anchor)

        self.label_success_name.place(x=150, y=60, anchor=anchor)
        self.label_error_name.place(x=150, y=90, anchor=anchor)
        self.label_success_val.place(x=210, y=60, anchor=anchor)
        self.label_error_val.place(x=210, y=90, anchor=anchor)

        self.label_serial_code.place(x=150, y=120, anchor=anchor)

        self.scrollbar.place(x=530, y=128, height=184, anchor=anchor)
        self.boot_list.config(yscrollcommand=self.scrollbar.set)
        self.boot_list.place(x=516, y=128, anchor=anchor)

    def entry_key(self, event):
        keycode = event.keycode
        key_val = event.char
        # print(event)
        if keycode == 13 and len(self.serial_code) > 0:
            item_bg = "green"
            self.set_serial_code_time(self.serial_code)
            if int(self.serial_code) == 1:
                res = subprocess.call("../exe/error.exe")
                item_bg = "red"
            else:
                res = subprocess.call("../exe/success.exe")

            if res:
                self.error_count += 1
                res = "error"
                print("error")
            else:
                self.success_count += 1
                res = "success"
                print("success")

            # 添加日志
            logger("%s          %s\r\n" % (self.serial_code, res))

            self.boot_list.insert(self.list_index, "%s                  %s" % (self.serial_code, res))
            self.boot_list.itemconfigure(self.list_index, fg=item_bg)
            self.boot_list.yview_moveto(self.list_index)
            self.label_success_val['text'] = self.success_count
            self.label_error_val['text'] = self.error_count

            self.list_index += 1
            self.serial_code = ""
        elif key_val.isdigit():
            self.serial_code += key_val

    def set_serial_code_time(self, code):
        if code is not None and len(code) >= 16:
            year = "20%s" % code[6:8]
            week = int(code[8:10])
            week_day = int(code[10:12])
            print(year, week, week_day)
            # self.label_time_value['text'] = ""

    def run(self):
        self.root.mainloop()


BootRecord().run()

