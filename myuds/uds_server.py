#!/usr/bin/env python
# -*- coding:utf-8 -*-


import config
import zmq
import time
import binascii
from protobuf import can_pb2
from common import cim_utils as cu


class Download:
    def __init__(self):
        self.is_run = True
        self.uds_cfg = config.UDS()
        self.zmq_cfg = config.Zmq()
        self.recv_data = ""

    def start(self):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://%s:%s" % (self.zmq_cfg.zmq_ip, self.zmq_cfg.zmq_port))
        socket.setsockopt(zmq.LINGER, 5000)  # 请求等待5秒钟

        while self.is_run:
            msg = socket.recv()
            if msg is not None:
                can_info = can_pb2.UDSData()
                can_info.ParseFromString(msg)
                # arbitration_id = hex(can_info.arbitration_id).upper()
                hex_data = can_info.data

                pci = hex_data[0:2]

                # print pci
                # print data

                if self.uds_cfg.SF == int(pci[0]):
                    data = hex_data[2:]
                    self.recv_data
                    print('SF:', cu.Convert.hex_list_to_str(data))
                    socket.send('0')
                elif self.uds_cfg.FF == int(pci[0]):
                    data = hex_data[4:]
                    print('FF:', cu.Convert.hex_list_to_str(data))
                    socket.send('654321')


Download().start()

