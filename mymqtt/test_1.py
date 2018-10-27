#!/usr/bin/env python
# -*- coding:utf-8 -*-

import paho.mqtt.client as mqtt
import time
import random


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc)+'\n')


def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload)+'\n')


client = mqtt.Client(client_id="test_1")
client.username_pw_set("ducl", "123456")
client.on_connect = on_connect
client.on_message = on_message
client.connect("127.0.0.1", 1883)
client.loop_start()


while True:
    client.publish("info", random.randint(0, 10))
    time.sleep(1)

    client.subscribe("info")





