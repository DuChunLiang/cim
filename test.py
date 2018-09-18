#!/usr/bin/env python
# -*- coding:utf-8 -*-

from protobuf import can_pb2
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

can_info = can_pb2.CanInfo()
can_info.timestamp = 1564156456.31
can_info.arbitration_id = '1235'
can_info.sign_name = '45a6sdf'
can_info.sign_value = 100.1
can_info.cycle_time = 20
can_info.minimum = 1000
can_info.maximum = -500

ci = can_pb2.CanInfo()
ci.CopyFrom(can_info)
print ci.SerializeToString()

