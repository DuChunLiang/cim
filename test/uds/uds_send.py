#!/usr/bin/env python

import sys
import can
from udstools import udstools


class UdsTest:
    def __init__(self, channel):
        self.channel = channel

    @staticmethod
    def str_to_hex(s):
        return ''.join([hex(ord(c)).replace('0x', '') for c in s]).upper()

    def start(self):
        can.rc['interface'] = 'socketcan'
        can.rc['channel'] = self.channel
        can_bus = can.interface.Bus()
        uds = udstools.Uds(can_bus, 0x7e0, 0x7e8)  # ecu
        r = self.str_to_hex(sys.argv[2])
        uds.tp.send_pdu(bytearray.fromhex(r))
        # print(uds.ReadDataByIdent(int(sys.argv[2])))

    # @staticmethod
    # def read(v, len=4):
    #     uds.tp.send_pdu(struct.pack(">BBIH", 0x23, 0x24, v, len))
    #     r = uds.tp.get_pdu()
    #     if r[0] == 0x7f and r[2] == 0x31:
    #         return None
    #     assert r[0] == 0x63, r
    #     return r[1:]
    #
    # def read8(v):
    #     return struct.unpack("<B", read(v, 1))
    #
    # def read16(v):
    #     return struct.unpack("<H", read(v, 2))
    #
    # def read32(v):
    #     return struct.unpack("<I", read(v, 4))


UdsTest(sys.argv[1]).start()