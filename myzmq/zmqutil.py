#!/usr/bin/env python
# -*- coding:utf-8 -*-

import zmq


class ZmqUtil:

    def __init__(self):
        self._context = zmq.Context()
        self._poller = zmq.Poller()
        self._socket = None

    def init_pub(self, ip="127.0.0.1", port=5001):
        self._socket = self._context.socket(zmq.PUB)
        self._socket.bind("tcp://%s:%s" % (ip, port))

    def init_sub(self, ip="127.0.0.1", port=5001):
        self._socket = self._context.socket(zmq.SUB)
        self._socket.connect("tcp://%s:%s" % (ip, port))
        self._socket.setsockopt(zmq.SUBSCRIBE, '')
        self._poller.register(self._socket, zmq.POLLIN)

    def send(self, msg):
        if self._socket is not None:
            self._socket.send(msg)
        else:
            raise Exception('please run ZmqUtil.set_pub() in front of ZmqUtil.send()')

    def recv(self):
        res_val = None
        if self._poller is not None:
            for socket, event in self._poller.poll(0):
                res_val = socket.recv()
        else:
            raise Exception('please run ZmqUtil.set_sub() in front of ZmqUtil.recv()')
        return res_val
