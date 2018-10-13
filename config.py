#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 配置类


class Zmq:

    def __init__(self):
        self.zmq_ip = "127.0.0.1"
        self.zmq_port = 5000


class UDS:
    def __init__(self):
        self.SF = 0     # SingleFrame 单帧
        self.FF = 1     # FirstFrame 第一帧
        self.CF = 2     # ConsecutiveFrame 连续帧
        self.FC = 3     # FlowControl 流控制

    # 流控制状态
    class FCState:
        keep_on = 0
        wait = 1
        out_of = 2

        def __init__(self):
            pass







