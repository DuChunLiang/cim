#!/usr/bin/env python
# -*- coding:utf-8 -*-

# import cantools
# import struct
# import time
# import random


# from suds.client import Client
# import testmoped
#
#
# url = 'http://localhost:59990/moped/pws?wsdl'
# client = Client(url)
# client.options.cache.clear()
# s = client.service
#
# testmoped.uploadplus(s, "UltraSonicReader", "1.0")
# s.installApp("21UYA31581L000000", 506)

# print(struct.pack("6s", "酒店客房".encode(encoding="utf-8")))

# import cantools
# import can
#
# db = cantools.database.load_file("test.dbc")
# for m in db.messages:
#     print m.name
#
# can.rc['interface'] = 'socketcan'
# can.rc['channel'] = 'vcan0'
# can_bus = can.interface.Bus()
# while True:
#     bo = can_bus.recv()
#     res = db.decode_message(bo.arbitration_id, bo.data)
#     print res
# a = random.randint(0, 9)
#
# print(hex(0x123))
# print('%i%i%i' % a)

# c = configs.default_client_config['data_identifiers'][0xF190] = '>50s'
# # c['data_identifiers']
# d_i = c['data_identifiers']
# d_i[0xF190] = '>50s'
# print(c)
# id_l = []
# f = open('D:\lrzsz\candump-2018-09-01_114258_on_off.log', 'r')
# for d in f.readlines():
#     d_a = d.split(' ')
#     can_id = str(d_a[2]).split('#')[0]
#     # print(id_l)
#     if can_id not in id_l:
#         id_l.append(can_id)
#         print('%s %s %s' % (d_a[0], d_a[1], d_a[2]))

# db = cantools.database.load_file('dbc/J7.dbc')
# acc1 = db.get_message_by_name('ACC1')
# data = acc1.encode({'ACCMode': 0, 'ACCDistance': 0, 'TargetDetected': 1})
# print(acc1)
#
# ldw_fcm1 = db.get_message_by_name('LDW_FCW1')
# data = ldw_fcm1.encode({'DSMWarningStatus': 0, 'LDWStatus': 2})
# print(data)

# fli1 = db.get_message_by_name('FLI1')
# data = fli1.encode({'laneRedLeft': 1})
# print(data)

# ccvs = db.get_message_by_name('CCVS')
# data = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00')
# print(data)
# v = struct.pack('<H', int(200/0.003906))
# data[1] = v[0]
# data[2] = v[1]
# # print(v[len(v)-4:len(v)-2])
# # a = b'\x00\%x\%x\x00\x00\x00\x00\x00' % (v[len(v)-2:len(v)], v[len(v)-3:len(v)-2])
# print(v)
# print(bytes(data))


# ecu1 = db.get_message_by_name('ECU1')
# data = ecu1.encode({'S_EngineSpeed': 20})
# print(data)


# a = struct.pack('<HBB2H', 0, 0, 16, 0, 0)
# print(int(0.07*100))
#
# for i in range(10):
#     print(random.randint(1000, 3000))


# a = binascii.crc32("123456".encode())
# v = "%i%i%i" % (int())bytes(0x313238).decode("ascii")

# v = binascii.a2b_hex('8000aabb'.encode())

# print(bytes(hex(int(0x8000aabb & 0xffffffff)).encode()))
# print(hex(binascii.crc32(b'\x80\x00\xaa\xbb') & 0xffffffff))
# import binascii
# a = 879
# c = "%04X" % a
# print(c)
# d = bytearray.fromhex(c)
# d[1] = d[1] & 0xF0
# print(d)
# print(int(binascii.b2a_hex(d), 16))
# a = 3.721159420289855
# a = b'\x01\x00\x00\x00\x01\x13a\x00\x00\x00v\r~\x10\n'
# b = b'~\x10\n\x01\x00\x00\x00\x00\x10\xe4\x10\x00\x00\x05\r'

# restart_count = 0
# f = open(r"D:\lrzsz\restart_count.log", "r")
# count = f.readline()
# if count is not None and len(count) > 0:
#     restart_count = int(count)
#     print('--', len(count))
# print(restart_count)
# f.close()
import subprocess

# res = subprocess.getstatusoutput("D:\lrzsz\BOOT\CanBoot\canbootcli.exe -n IC216_Boot.mhx")
# res = subprocess.call("D:\lrzsz\BOOT\CanBoot\canbootcli.exe -n D:\lrzsz\BOOT\CanBoot\IC216_Boot.mhx")
# command = "D:\lrzsz\BOOT\CanBoot\canbootcli.exe -n=1 -q D:\lrzsz\BOOT\CanBoot\IC216_Boot.mhx"
# res = subprocess.call(command)
# p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# lines = []
# for line in iter(p.stdout.readline, b''):
#     line = line.rstrip().decode('utf8')
#     print(">>>", line)
#     lines.append(line)
# print(res)
# print('---', memo)
# out = open()
# p = "D:\lrzsz\R.java"
# f = open(p, "r+")
# for d in f.readlines():
#     if len(d) > 0 and "=" in d:
#         val = d[-12:len(d)-2]
#         if val.isdigit():
#             out_val = "%s%s" % (d[:len(d)-12], str(hex(int(val))))
#             # d[:len(d)-2] = str(hex(int(val)))
#             print(out_val)
#         else:
#             print(d)
#     else:
#         print(d)
import time

# print(time.strptime("2018-01-01", "%Y-%m-%d"))
PAD = b'\xf1\x9e'
print(PAD)
