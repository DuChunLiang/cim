#!/usr/bin/env python
# -*- coding:utf-8 -*-

import zmq
import time
import threading
import matplotlib.pyplot as plt
import matplotlib.animation as animation


# 日志打印信息
def logger(content):
    now_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print('%s-%s' % (now_date, content))


class CPO:
    x_temp_data, y_temp_data = 0., 0.  # x, y轴临时数据
    x_max_len = 1000      # x轴屏显长度
    listen_time = time.time()   # 监听接收消息时间
    time_out = 50  # 超时时间 ms
    minimum = 0     # 最小值
    maximum = 5000  # 最大值
    is_recv = False   # 是否已经接收过数据
    test = time.time()

    def __init__(self):
        self.a = ''

    # 获取zmq接收消息时间间隔
    def get_interval_time(self):
        return int((time.time() - self.listen_time) * 1000)


# zmq接受消息
class ZmqSub:

    def __init__(self):
        self.a = ''

    def start(self):
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        print("Collecting updates from weather server...")
        socket.connect("tcp://192.168.8.130:5000")
        socket.setsockopt(zmq.SUBSCRIBE, '')

        while True:
            msg = socket.recv()
            msg_list = str(msg).split('|')
            # 生成报文时的时间戳，ID, 名字, 值，消息发送频率（ms）
            timestamp, id, name, value, \
            cycle_time, minimum, maximum = msg_list[0], msg_list[1], msg_list[2], \
                                           msg_list[3], msg_list[4], msg_list[5], msg_list[6]

            CPO.listen_time = time.time()
            CPO.y_temp_data = float(value)

            if float(cycle_time) > 0:
                CPO.time_out = float(cycle_time)
            CPO.minimum = minimum
            CPO.maximum = maximum
            CPO.is_recv = True


# 绘图
class Drawing:
    def __init__(self):
        self.a = ''

    def start(self):
        fig, ax = plt.subplots()
        x_data, y_data, c_data = [], [], []

        def init():
            ax.set_xlim(0, CPO.x_max_len)
            print(CPO.minimum, '---', CPO.maximum)
            ax.set_ylim(CPO.minimum, CPO.maximum)
            scat = ax.scatter(x_data, y_data, c=c_data, s=1)
            return scat,

        def update(frame):

            if len(x_data) <= CPO.x_max_len:
                x_data.append(frame)
                # CPO.x_temp_data += int((time.time() - CPO.test_time) * 1000)
                # CPO.test_time = time.time()

            y_data.append(CPO.y_temp_data)

            if len(y_data) > CPO.x_max_len+1:
                y_data.pop(0)

            # print('---', float(frame) * 20)
            if CPO().get_interval_time() > CPO.time_out:
                c_data.append('r')
            else:
                c_data.append('b')

            if len(c_data) > CPO.x_max_len+1:
                c_data.pop(0)

            scat = ax.scatter(x_data, y_data, c=c_data, s=1)

            # print('---', int((time.time() - CPO.test_time) * 1000))

            return scat,

        ani = animation.FuncAnimation(fig=fig, func=update, frames=range(0, CPO.x_max_len + 1),
                                      init_func=init, blit=True, interval=0)
        plt.xlabel("s")
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
    # while not CPO.is_recv:
    #     time.sleep(1)

    t_draw.start()
    logger('main-启动绘图线程 %s' % thread_name)

    t_draw.join()


main()








