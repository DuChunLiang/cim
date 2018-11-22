#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import time
import subprocess
import threading
if sys.version_info.major == 2:
    import Tkinter as tk
else:
    import tkinter as tk
    from tkinter.scrolledtext import ScrolledText


log_path = r"D:\lrzsz\boot.log"


# 日志打印信息
def logger(content):
    now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    content = '%s - %s' % (now_date, content)
    # print(content)
    log_f = open(log_path, "a")
    log_f.write(content)
    log_f.close()


class BootRecord:

    def __init__(self, width=1200, higth=600):
        self.serial_code = ""
        self.bg = "#C7EDCC"
        self.list_index = 0
        self.success_count = 0
        self.error_count = 0

        self.is_run_command = False

        self.root = tk.Tk()
        self.root.title('Boot Run Tool')
        self.root.configure(bg=self.bg)
        self.root.resizable(0, 0)
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw-width) / 2
        y = (sh-higth) / 2
        self.root.geometry("%dx%d+%d+%d" % (width, higth, x, y))

        self.scrollbar = tk.Scrollbar(self.root)
        self.label_serial_code = tk.Label(self.root, text='Serial Code:', bg=self.bg)
        self.label_text_console_name = tk.Label(self.root, text='Console:', bg=self.bg)

        self.label_success_name = tk.Label(self.root, text='Success Count:', bg=self.bg)
        self.label_error_name = tk.Label(self.root, text='Error Count:', bg=self.bg)
        self.product_mode_name = tk.Label(self.root, text='Product Mode:', bg=self.bg)
        self.hw_version_name = tk.Label(self.root, text='HW Version:', bg=self.bg)
        self.sw_version_name = tk.Label(self.root, text='SW Version:', bg=self.bg)
        self.product_serial_name = tk.Label(self.root, text='Product Serial:', bg=self.bg)

        self.label_success_val = tk.Label(self.root, text='0', bg=self.bg)
        self.label_error_val = tk.Label(self.root, text='0', bg=self.bg)
        self.product_mode_val = tk.Label(self.root, text='0', bg=self.bg)
        self.hw_version_val = tk.Label(self.root, text='0', bg=self.bg)
        self.sw_version_val = tk.Label(self.root, text='0', bg=self.bg)
        self.product_serial_val = tk.Label(self.root, text='0000', bg=self.bg)

        self.label_time = tk.Label(self.root, text='Time:', bg=self.bg)
        self.label_time_value = tk.Label(self.root, text='2018-01-03', bg=self.bg)
        self.boot_list = tk.Listbox(self.root, width=60, bg=self.bg)

        self.text_console = ScrolledText(self.root, width=60, bg=self.bg)

        self.control_option()

    def control_option(self):
        anchor = "ne"

        self.root.focus()
        self.root.bind("<Key>", self.entry_key)

        self.label_time.place(x=150, y=30, anchor=anchor)
        self.label_time_value.place(x=230, y=31, anchor=anchor)

        self.label_success_name.place(x=150, y=60, anchor=anchor)
        self.label_error_name.place(x=150, y=90, anchor=anchor)
        self.product_mode_name.place(x=400, y=30, anchor=anchor)
        self.hw_version_name.place(x=400, y=60, anchor=anchor)
        self.sw_version_name.place(x=400, y=90, anchor=anchor)
        self.product_serial_name.place(x=650, y=30, anchor=anchor)

        self.label_success_val.place(x=210, y=60, anchor=anchor)
        self.label_error_val.place(x=210, y=90, anchor=anchor)
        self.product_mode_val.place(x=460, y=30, anchor=anchor)
        self.hw_version_val.place(x=460, y=60, anchor=anchor)
        self.sw_version_val.place(x=460, y=90, anchor=anchor)
        self.product_serial_val.place(x=710, y=30, anchor=anchor)

        self.label_serial_code.place(x=150, y=120, anchor=anchor)

        self.scrollbar.place(x=590, y=128, height=400, anchor=anchor)
        self.scrollbar.config(command=self.boot_list.yview)
        self.boot_list.config(yscrollcommand=self.scrollbar.set)
        self.boot_list.place(x=576, y=128, height=400, anchor=anchor)

        self.label_text_console_name.place(x=650, y=120, anchor=anchor)
        self.text_console.place(x=1100, y=128, height=400, anchor=anchor)

    def run_command(self):
        item_bg = "green"
        # command = "D:\lrzsz\BOOT\CanBoot\canbootcli.exe -n=1 D:\lrzsz\BOOT\CanBoot\IC216_Boot.mhx"
        run_res = True
        # popen = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        # for line in iter(popen.stdout.readline, b''):
        #     line = line.rstrip().decode('utf8')
        #     print(">>>", line)
        #     self.text_console.insert(tk.END, "%s\r\n" % line.replace("\x08", ""))
        #     if "ERROR" in line:
        #         run_res = False
        #         subprocess.call("taskkill -im canbootcli.exe -f")

        # print('---', run_res)
        # 填写控制台日志
        if run_res:
            self.success_count += 1
            res = "SUCCESS"
            # print("success")
        else:
            item_bg = "red"
            self.error_count += 1
            res = "ERROR"
            # print("error")

        # 添加日志
        logger("%s          %s\r\n" % (self.serial_code, res))

        self.boot_list.delete(self.list_index)
        now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        self.boot_list.insert(self.list_index, "%s          %s          %s"
                              % (now_date, self.serial_code, res))
        self.boot_list.itemconfigure(self.list_index, fg=item_bg)

        self.boot_list.yview_moveto(self.list_index)
        self.scrollbar.activate(self.list_index)
        print('-----', self.scrollbar.get(), self.list_index)
        self.label_success_val['text'] = self.success_count
        self.label_error_val['text'] = self.error_count

        self.list_index += 1
        self.serial_code = ""
        self.is_run_command = False

    def entry_key(self, event):
        keycode = event.keycode
        key_val = event.char
        if not self.is_run_command:
            if keycode == 13 and len(self.serial_code) > 0:
                self.is_run_command = True
                self.text_console.delete('1.0', 'end')
                now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                self.analysis_serial_code(self.serial_code)
                self.boot_list.insert(self.list_index, "%s          %s          %s"
                                      % (now_date, self.serial_code, "RUNNING"))
                self.boot_list.itemconfigure(self.list_index, fg="goldenrod")

                run_command_t = threading.Thread(target=self.run_command, name="run_command")
                run_command_t.setDaemon(True)
                run_command_t.start()

            elif key_val.isdigit():
                self.serial_code += key_val

    def analysis_serial_code(self, code):
        if code is not None and len(code) >= 16:
            product_mode = int(code[0:2])
            if product_mode == 11:
                product_mode = "IC216"
            elif product_mode == 12:
                product_mode = "IC218"
            elif product_mode == 21:
                product_mode = "IM218"
            elif product_mode == 22:
                product_mode = "IM228"

            hw_version = "%s.%s" % (code[2:3], code[3:4])
            sw_version = "%s.%s" % (code[4:5], code[5:6])
            year = "20%s" % code[6:8]
            week = int(code[8:10])
            week_day = int(code[10:12])
            product_serial = code[12:17]
            date = "%s-%s-%s" % (year, week, week_day)
            self.label_time_value['text'] = time.strftime("%Y-%m-%d", time.strptime(date, '%Y-%U-%w'))
            self.product_mode_val['text'] = product_mode
            self.hw_version_val['text'] = hw_version
            self.sw_version_val['text'] = sw_version
            self.product_serial_val['text'] = product_serial

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    BootRecord().run()

