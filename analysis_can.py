#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import time
import cantools
import can
import config
from protobuf import can_pb2
from myzmq import zmqutil


# 日志打印信息
def logger(content):
    now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print('%s - %s' % (now_date, content))


class CPO:
    dbc_id_list = []       # dbc信息存储 用于判断id是否存在

    def __init__(self):
        print ('')


class Analysis:

    def __init__(self):
        print('')

    # 判断id在dbc文件中是否存在
    def id_is_exist(self, _id):
        ret = True if _id in CPO.dbc_id_list else False
        return ret

    # 解析can消息
    def analysis_can(self):
        logger("已启动can数据解析")
        cf = config.Config()
        zu = zmqutil.ZmqUtil()
        zu.init_pub(ip=cf.zmq_ip, port=cf.zmq_port)

        # 加载dbc文件
        db = cantools.database.load_file('dbc/db.dbc')
        # 存入dbc文件中所有id 用于判断传入id在dbc中是否存在
        for m in db.messages:
            CPO.dbc_id_list.append(m.frame_id)

        can.rc['interface'] = 'socketcan'
        can.rc['channel'] = sys.argv[1]
        can_bus = can.interface.Bus()
        while True:
            CPO.test_time = time.time()
            bo = can_bus.recv()

            frame_id = bo.arbitration_id
            data = (bo.data + bytearray('0000000000000000'.encode()))[:16]

            # 判断id是否存在
            if self.id_is_exist(frame_id):
                if frame_id == 201:
                    res = db.decode_message(frame_id, data)
                    if res is not None:
                        send_msg = self._get_send_msg(db.get_message_by_frame_id(frame_id), bo, res, 'EngSpd')
                        zu.send(send_msg)
            # else:
            #     print('-------%s在dbc文件中不存在-------' % frame_id)\

    # 获取发送信息
    def _get_send_msg(self, dbc_message, bo, res, name):
        cycle_time = dbc_message.cycle_time  # 获取发包间隔时间
        dbc_sg = dbc_message.get_signal_by_name(name)
        minimum = dbc_sg.minimum
        maximum = dbc_sg.maximum
        value = res[name]

        # protobuf交互协议
        can_info = can_pb2.CanInfo()
        can_info.timestamp = bo.timestamp
        can_info.arbitration_id = str(bo.arbitration_id)
        can_info.sign_name = name
        can_info.sign_value = value
        can_info.cycle_time = cycle_time
        can_info.minimum = minimum
        can_info.maximum = maximum
        print(value)
        return can_info.SerializeToString()


if __name__ == "__main__":
    Analysis().analysis_can()





