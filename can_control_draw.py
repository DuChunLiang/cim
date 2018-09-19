#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
import threading
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from protobuf import can_pb2
from myzmq import zmqutil
import config


# 日志打印信息
def logger(content):
    now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print('%s-%s' % (now_date, content))


class CPO:
    x_temp_data, y_temp_data = 0., 0.  # x, y轴临时数据
    x_max_len = 1000  # x轴屏显长度
    time_out = 0  # 超时时间 ms
    minimum = 0  # 最小值
    maximum = 5000  # 最大值
    is_recv = False  # 是否已经接收过数据
    y_value = maximum/2
    listen_time = time.time()  # 监听接收消息时间

    def __init__(self):
        self.t = None

    # 获取zmq接收消息时间间隔
    def get_interval_time(self):
        return int((time.time() - self.listen_time) * 1000)


# zmq接受消息
class ZmqSub:

    def __init__(self):
        _cf = config.Config()
        self.zu = zmqutil.ZmqUtil()
        self.zu.init_sub(ip=_cf.zmq_ip, port=_cf.zmq_port)

    def start(self):
        while True:
            res_msg = self.zu.recv()
            if res_msg:
                can_info = can_pb2.CanInfo()
                can_info.ParseFromString(res_msg)

                # 生成报文时的时间戳，ID, 名字, 值，消息发送频率（ms）
                timestamp, arbitration_id, name, value, \
                cycle_time, minimum, maximum = can_info.timestamp, can_info.arbitration_id, \
                                               can_info.sign_name, can_info.sign_value, \
                                               can_info.cycle_time, can_info.minimum, can_info.maximum

                CPO.listen_time = time.time()
                if float(cycle_time) > 0:
                    CPO.time_out = float(cycle_time)

                CPO.y_value = value


# 绘图
class Drawing:
    def __init__(self):
        self.y_value = 1

    def start(self):
        fig, ax = plt.subplots()
        x_data, y_data, c_data = [], [], []

        def init():
            ax.set_xlim(0, CPO.x_max_len)
            ax.set_ylim(CPO.minimum, CPO.maximum)
            scat = ax.scatter(x_data, y_data, c=c_data, s=1)
            return scat,

        def update(frame):
            CPO.test_time = time.time()
            if len(x_data) <= CPO.x_max_len:
                x_data.append(frame)

            y_data.append(CPO.y_value)
            if len(y_data) > CPO.x_max_len+1:
                y_data.pop(0)

            # 根据周期好描述判断是否超时并设定颜色
            if CPO().get_interval_time() > CPO.time_out:
                c_data.append('r')
            else:
                c_data.append('b')

            if len(c_data) > CPO.x_max_len+1:
                c_data.pop(0)

            scat = ax.scatter(x_data, y_data, c=c_data, s=1)
            return scat,

        ani = animation.FuncAnimation(fig=fig, func=update, frames=range(0, CPO.x_max_len + 1),
                                      init_func=init, blit=True, interval=0)
        plt.xlabel("Hz")
        plt.ylabel("r/min")
        plt.grid(True)
        plt.show()


def main():
    thread_name = "threading-zmq"
    t_zmq = threading.Thread(target=ZmqSub().start, name=thread_name)
    t_zmq.setDaemon(True)

    thread_name = "threading-draw"
    t_draw = threading.Thread(target=Drawing().start, name=thread_name)
    t_draw.setDaemon(True)

    t_zmq.start()
    logger('main-启动zmq接受数据线程 %s' % thread_name)
    time.sleep(1)

    t_draw.start()
    logger('main-启动绘图线程 %s' % thread_name)

    t_draw.join()


if __name__ == "__main__":
    main()








