#!/usr/bin/env python
# -*- coding:utf-8 -*-

import cantools
import struct
import time

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

db = cantools.database.load_file('dbc/J7.dbc')
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


a = struct.pack('<HBB2H', 0, 0, 16, 0, 0)
print(int(0.07*100))
