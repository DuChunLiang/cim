#!/usr/bin/env python

import sys
import can
from . import udstools


class UdsTest:
    def __init__(self, channel):
        self.channel = channel

    def start(self):
        can.rc['interface'] = 'socketcan'
        can.rc['channel'] = self.channel
        can_bus = can.interface.Bus()
        uds = udstools.Uds(can_bus, 0x7e8, 0x7e0)  # ecu
        print(uds.tp.get_pdu())
        # print(uds.ReadDataByIdent(int(sys.argv[2])))


UdsTest(sys.argv[1]).start()