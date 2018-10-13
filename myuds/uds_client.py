#!/usr/bin/env python
# -*- coding:utf-8 -*-

import zmq
import time
import config
from protobuf import can_pb2
from common import cim_utils as cu


class Temp:
    def __init__(self):
        pass

    data = "www.baidu.com, lalalalalla, iso, 0972313"
    # data = "ISO"


class Upload:
    def __init__(self):
        self.is_run = True
        self.uds_cfg = config.UDS()
        self.zmq_cfg = config.Zmq()
        self.upload_data = cu.Convert.str_to_hex_list(Temp.data)
        self.upload_data_len = len(self.upload_data)
        self.cursor = 0

    @staticmethod
    def _create_data(name='UDS', arbitration_id=None, data=None):
        uds_data = can_pb2.UDSData()
        uds_data.arbitration_id = arbitration_id
        uds_data.name = name
        uds_data.data = data
        return uds_data.SerializeToString()

    def _list_to_hex(self, pci="", length=0):
        data = "%s%s" % (pci, ''.join('%s' % x for x in self.upload_data[self.cursor:self.cursor+length]).upper())
        return data

    def start(self):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://%s:%s" % (self.zmq_cfg.zmq_ip, self.zmq_cfg.zmq_port))
        socket.setsockopt(zmq.LINGER, 5000)  # 请求等待5秒钟

        # 判断是单帧传输方式还是多帧传输方式
        if self.upload_data_len < 7:
            pci = '%s%s' % (self.uds_cfg.SF, self.upload_data_len)
            data = self._list_to_hex(pci, self.upload_data_len)

            socket.send(self._create_data(arbitration_id=0x7E0, data=data))
        else:
            # while self.is_run:
            # 游标为0时 发送FirstFrame格式信息
            if self.cursor == 0:
                pci = '%s%03x' % (self.uds_cfg.FF, self.upload_data_len)
                data = self._list_to_hex(pci, 6)

                msg = self._create_data(arbitration_id=0x7E0, data=data)
                self.cursor += 6


            socket.send(msg)

            response = socket.recv()


# Upload().start()

a = ""

for i in range(6):
    a.join(str(i))
    # print str(i)
