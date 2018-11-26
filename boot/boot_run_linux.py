#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
import time
import subprocess
import threading
import platform
if sys.version_info.major == 2:
    import Tkinter as tk
else:
    import tkinter as tk
    from tkinter.scrolledtext import ScrolledText
    from tkinter.filedialog import askopenfilename
    from tkinter import messagebox
    from tkinter import ttk


class Constant:
    RUNNING = ["RUNNING", "goldenrod"]
    SUCCESS = ["SUCCESS", "green"]
    ERROR = ["ERROR", "red"]
    RESET = ["RESET", "blue"]
    TIMEOUT = ["TIMEOUT", "blueviolet"]


class CPO:
    log_path = r"/home/pi/canboot-%s.csv" % time.strftime('%Y-%m-%d', time.localtime(time.time()))
    # log_path = r"canboot-%s.csv" % time.strftime('%Y-%m-%d', time.localtime(time.time()))
    error_log_path = r"/home/pi/canboot-error-%s.log" % time.strftime('%Y-%m-%d', time.localtime(time.time()))
    # command_path = "D:\lrzsz\CANBoot\CanBoot/"
    command_path = "/home/pi/work/openblt/Host/"
    product_mode = ""
    run_res = Constant.SUCCESS[0]
    run_common_time = time.time()
    is_listen_run_command = False
    last_choose_file = ""


# 日志打印信息
def logger(content):
    now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    content = '%s,%s' % (now_date, content)
    print(content)
    log_f = open(CPO.log_path, "a")
    log_f.write(content)
    log_f.close()


def logger_error(content):
    now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    content = '%s - %s' % (now_date, content)
    # print(content)
    log_f = open(CPO.error_log_path, "a")
    log_f.write(content)
    log_f.close()


class BootRecord:

    def __init__(self, width=1800, higth=900):
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
        # width = sw
        # higth = sh
        x = (sw-width) / 2
        y = (sh-higth) / 2
        self.root.geometry("%dx%d+%d+%d" % (width, higth, x, y))

        self.scrollbar = tk.Scrollbar(self.root)
        self.label_serial_code = tk.Label(self.root, text='Serial Code:', bg=self.bg)
        self.label_text_console_name = tk.Label(self.root, text='Console:', bg=self.bg)

        self.label_success_name = tk.Label(self.root, text='Success Count:', bg=self.bg)
        self.label_error_name = tk.Label(self.root, text='Fail Count:', bg=self.bg)
        self.product_mode_name = tk.Label(self.root, text='Product Mode:', bg=self.bg)
        self.hw_version_name = tk.Label(self.root, text='HW Version:', bg=self.bg)
        self.sw_version_name = tk.Label(self.root, text='SW Version:', bg=self.bg)
        self.product_serial_name = tk.Label(self.root, text='Product Serial:', bg=self.bg)
        self.label_file_name = tk.Label(self.root, text='File Path:', bg=self.bg)
        self.label_type_radio_name = tk.Label(self.root, text='Type:', bg=self.bg)
        self.label_node_combobox_name = tk.Label(self.root, text='Node:', bg=self.bg)

        self.label_success_val = tk.Label(self.root, text='0', bg=self.bg)
        self.label_error_val = tk.Label(self.root, text='0', bg=self.bg)
        self.product_mode_val = tk.Label(self.root, text='0', bg=self.bg)
        self.hw_version_val = tk.Label(self.root, text='0', bg=self.bg)
        self.sw_version_val = tk.Label(self.root, text='0', bg=self.bg)
        self.product_serial_val = tk.Label(self.root, text='0000', bg=self.bg)
        self.type_radio_val = tk.StringVar()    # 烧写类型单选按钮
        self.node_combobox_val = tk.StringVar()  # 节点选择值

        self.file_entry_var = tk.StringVar()
        self.file_btn = tk.Button(self.root, text="Choose File", command=self.choose_file)

        self.label_time = tk.Label(self.root, text='Serial Code Date:', bg=self.bg)
        self.label_time_value = tk.Label(self.root, text='2018-01-03', bg=self.bg)
        self.boot_list = tk.Listbox(self.root, width=60, bg=self.bg)

        self.text_console = ScrolledText(self.root, width=80, bg=self.bg)

        self.reset_btn = tk.Button(self.root, text="Reset", width=12, command=self.reset_run)

        self.control_option()

    def control_option(self):
        anchor = "ne"

        self.root.focus()
        self.root.bind("<KeyPress>", self.entry_key)

        self.label_time.place(x=150, y=30, anchor=anchor)
        self.label_time_value.place(x=230, y=31, anchor=anchor)

        self.label_success_name.place(x=150, y=60, anchor=anchor)
        self.label_error_name.place(x=150, y=90, anchor=anchor)
        self.product_mode_name.place(x=400, y=30, anchor=anchor)
        self.hw_version_name.place(x=400, y=60, anchor=anchor)
        self.sw_version_name.place(x=400, y=90, anchor=anchor)
        self.product_serial_name.place(x=650, y=30, anchor=anchor)
        self.label_file_name.place(x=650, y=60, anchor=anchor)
        self.label_type_radio_name.place(x=650, y=90, anchor=anchor)

        self.label_success_val.place(x=210, y=60, anchor=anchor)
        self.label_error_val.place(x=210, y=90, anchor=anchor)
        self.product_mode_val.place(x=460, y=30, anchor=anchor)
        self.hw_version_val.place(x=460, y=60, anchor=anchor)
        self.sw_version_val.place(x=460, y=90, anchor=anchor)
        self.product_serial_val.place(x=710, y=30, anchor=anchor)

        file_entry = tk.Entry(self.root, textvariable=self.file_entry_var, width=40, bg="white", state="readonly")

        file_entry.place(x=980, y=60, anchor=anchor)
        self.file_btn.place(x=1110, y=56, anchor=anchor)

        self.label_serial_code.place(x=150, y=120, anchor=anchor)

        type_radio_1 = tk.Radiobutton(self.root, text="File",
                                      variable=self.type_radio_val, value="1", command=self.radio_function)
        type_radio_1.select()
        type_radio_2 = tk.Radiobutton(self.root, text="Code",
                                      variable=self.type_radio_val, value="2", command=self.radio_function)

        type_radio_1.place(x=742, y=86, anchor=anchor)
        type_radio_2.place(x=850, y=86, anchor=anchor)

        node_combobox = ttk.Combobox(self.root, width=6, textvariable=self.node_combobox_val, state='readonly')
        node_combobox["values"] = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
        node_combobox.current(0)
        node_combobox.place(x=1020, y=90, anchor=anchor)
        self.label_node_combobox_name.place(x=950, y=90, anchor=anchor)

        self.scrollbar.place(x=650, y=124, height=400, anchor=anchor)
        self.scrollbar.config(command=self.boot_list.yview)
        self.boot_list.config(yscrollcommand=self.scrollbar.set)
        self.boot_list.place(x=636, y=124, height=400, anchor=anchor)

        self.label_text_console_name.place(x=730, y=120, anchor=anchor)
        self.text_console.config(state=tk.DISABLED)
        self.text_console.place(x=1324, y=124, height=400, anchor=anchor)
        self.reset_btn.pack(side=tk.BOTTOM, pady=30)

    def choose_file(self):
        file_path = askopenfilename()
        if file_path is not None and len(file_path) > 0:
            file_suffix = str(file_path.split('.')[-1]).lower()
            # 判断后缀
            if file_suffix in ['s19', 'mhx', 'srec']:
                self.file_entry_var.set(file_path)
                CPO.last_choose_file = file_path
            else:
                messagebox.showwarning("提示", "请选择s19、mhx、srec格式文件!")

    def radio_function(self):
        if self.type_radio_val.get() == "1":
            self.file_btn.configure(state=tk.ACTIVE)
            self.file_entry_var.set(CPO.last_choose_file)
        else:
            self.file_btn.configure(state=tk.DISABLED)
            self.file_entry_var.set("")

    # 生成命令
    def get_command(self):
        run_file = "cbp"
        if self.type_radio_val.get() == "1":
            run_file = "canbootcli"

        node = " -n=%s" % self.node_combobox_val.get()

        command = CPO.command_path+run_file+node
        if CPO.product_mode == "IC216":
            command += " -d=can0 -sa=260000 -ss=20000"
        elif CPO.product_mode == "IC218" or CPO.product_mode == "IM218":
            command += " -d=can0 -sa=7F000 -ss=1000"
        elif CPO.product_mode == "IM228":
            command += " -d=can0 -q -sa=C000 -ss=2000"

        if self.type_radio_val.get() == "1":
            command += " -sn=%s %s" % (self.serial_code, self.file_entry_var.get())
        else:
            command += " -sn=%s" % self.serial_code

        return command

    def entry_key(self, event):
        keycode = event.keycode
        key_val = event.char
        # print('--', keycode, self.is_run_command, self.serial_code)
        if not self.is_run_command:
            if keycode == 36:
                if len(self.serial_code) == 16:
                    if (self.file_entry_var.get() is not None and len(self.file_entry_var.get()) > 0) \
                            or self.type_radio_val.get() == "2":
                        self.root.unbind("<KeyPress>")
                        self.text_console.config(state=tk.NORMAL)

                        self.text_console.delete('1.0', 'end')
                        now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        self.analysis_serial_code(self.serial_code)
                        self.boot_list.insert(self.list_index, "%s          %s          %s"
                                              % (now_date, self.serial_code, Constant.RUNNING[0]))
                        self.boot_list.itemconfigure(self.list_index, fg=Constant.RUNNING[1])

                        self.boot_list.yview_moveto(self.list_index)

                        self.is_run_command = True
                        CPO.is_listen_run_command = True
                        run_command_t = threading.Thread(target=self.run_command, name="run_command")
                        run_command_t.setDaemon(True)
                        run_command_t.start()

                        # listen_run_command_t = threading.Thread(target=self.listen_run_command,
                        #                                         name="listen_run_command")
                        # listen_run_command_t.setDaemon(True)
                        # listen_run_command_t.start()
                    else:
                        self.serial_code = ""
                        messagebox.showwarning("提示", "请选择烧写文件!")
                else:
                    self.serial_code = ""
                    self.is_run_command = False

            elif key_val.isdigit():
                self.serial_code += key_val

    def run_command(self):
        command = self.get_command()
        print(command)
        error_recode = ""
        popen = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        for line in iter(popen.stdout.readline, b''):
            CPO.run_common_time = time.time()
            line = line.rstrip().decode('utf8')

            line = line.replace("\x08", "").replace("\x1b", "") \
                .replace("[0m", "").replace("[32m", "") \
                .replace("[33m", "")

            error_recode += line
            self.text_console.insert(tk.END, "%s\n" % line)
            self.text_console.see(tk.END)
            if "ERROR" in line:
                CPO.run_res = Constant.ERROR[0]
                logger("%s,%s\r" % (self.serial_code, CPO.run_res))
                logger_error("%s,%s, %s\r" % (self.serial_code, CPO.run_res, error_recode))
                break

        CPO.is_listen_run_command = False
        self.killall_process()

        item_bg = ""
        # 填写控制台日志
        if CPO.run_res == Constant.SUCCESS[0]:
            self.success_count += 1
            item_bg = Constant.SUCCESS[1]
            print("success")
        elif CPO.run_res == Constant.ERROR[0]:
            item_bg = Constant.ERROR[1]
            self.error_count += 1
            print("error")
        elif CPO.run_res == Constant.RESET[0]:
            item_bg = Constant.RESET[1]
            self.error_count += 1
            print("reset")
        elif CPO.run_res == Constant.TIMEOUT[0]:
            item_bg = Constant.TIMEOUT[1]
            self.error_count += 1
            print("timeout")

        # 添加日志
        logger("%s,%s\r" % (self.serial_code, CPO.run_res))
        self.complete_run(CPO.run_res, item_bg)
        CPO.run_res = Constant.SUCCESS[0]

    # 监听烧写操作是否超时
    def listen_run_command(self):
        # print('---', self.is_run_command)
        CPO.run_common_time = time.time()
        while True:
            if self.is_run_command:
                if (time.time() - CPO.run_common_time) > 10:
                    CPO.run_res = Constant.TIMEOUT[0]
                    self.killall_process()
                    print("listen_run_command timeout")
                    break
            else:
                break

        print("listen_run_command end")

    # 完成运行后操作
    def complete_run(self, res, item_bg):
        self.boot_list.delete(self.list_index)
        now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        self.boot_list.insert(self.list_index, "%s          %s          %s"
                              % (now_date, self.serial_code, res))
        self.boot_list.itemconfigure(self.list_index, fg=item_bg)

        self.boot_list.yview_moveto(self.list_index)

        self.label_success_val['text'] = self.success_count
        self.label_error_val['text'] = self.error_count

        self.list_index += 1
        self.serial_code = ""
        self.text_console.config(state=tk.DISABLED)
        self.root.bind("<KeyPress>", self.entry_key)
        self.is_run_command = False

    def analysis_serial_code(self, code):
        if code is not None and len(code) >= 16:
            product_mode_hex = int(code[0:2])
            if product_mode_hex == 11:
                CPO.product_mode = "IC216"
            elif product_mode_hex == 12:
                CPO.product_mode = "IC218"
            elif product_mode_hex == 21:
                CPO.product_mode = "IM218"
            elif product_mode_hex == 22:
                CPO.product_mode = "IM228"

            hw_version = "%s.%s" % (code[2:3], code[3:4])
            sw_version = "%s.%s" % (code[4:5], code[5:6])
            year = "20%s" % code[6:8]
            week = int(code[8:10])
            week_day = int(code[10:12])
            product_serial = code[12:17]
            date = "%s-%s-%s" % (year, week, week_day)
            self.label_time_value['text'] = time.strftime("%Y-%m-%d", time.strptime(date, '%Y-%U-%w'))
            self.product_mode_val['text'] = CPO.product_mode
            self.hw_version_val['text'] = hw_version
            self.sw_version_val['text'] = sw_version
            self.product_serial_val['text'] = product_serial

    # 杀掉运行命令进程
    @staticmethod
    def killall_process():
        sysstr = platform.system()
        if sysstr == "Windows":
            subprocess.Popen("taskkill -im canbootcli.exe -f", shell=True)
            subprocess.Popen("taskkill -im cbp.exe -f", shell=True)
        else:
            subprocess.Popen("killall -9 cbp", shell=True)
            subprocess.Popen("killall -9 canbootcli", shell=True)

    # 重置can驱动
    @staticmethod
    def reset_can():
        subprocess.Popen("sudo ip link set can0 down", shell=True)
        time.sleep(1)
        subprocess.Popen("sudo ip link set can0 type can bitrate 250000", shell=True)
        subprocess.Popen("sudo ip link set can0 up", shell=True)
        print("reset can driver success")

    # 重置操作
    def reset_run(self):
        self.killall_process()
        self.reset_can()
        if self.is_run_command:
            CPO.run_res = Constant.RESET[0]

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    BootRecord().run()

