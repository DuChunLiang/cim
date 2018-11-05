#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
from canlib import canlib, kvadblib

bitrates = {
    '1M': canlib.canBITRATE_1M,
    '500K': canlib.canBITRATE_500K,
    '250K': canlib.canBITRATE_250K,
    '125K': canlib.canBITRATE_125K,
    '100K': canlib.canBITRATE_100K,
    '62K': canlib.canBITRATE_62K,
    '50K': canlib.canBITRATE_50K,
    '83K': canlib.canBITRATE_83K,
    '10K': canlib.canBITRATE_10K,
}


def printframe(db, frame):
    try:
        bmsg = db.interpret(frame)
    except kvadblib.KvdNoMessage:
        print("<<< No message found for frame with id %s >>>" % frame.id)
        return

    msg = bmsg._message

    # form = '═^' + str(width)
    # print(format(" %s " % msg.name, form))

    print('┏', msg.name)

    if msg.comment:
        print('┃', '"%s"' % msg.comment)

    for bsig in bmsg:
        print('┃', bsig.name + ':', bsig.value, bsig.unit)

    print('┗')


class KvaserCan:

    def __init__(self):
        self.dbc_file = "../dbc/adc_ldc.dbc"

    @staticmethod
    def set_up_channel(self, channel=0, open_flags=canlib.Open.ACCEPT_VIRTUAL,
                       bitrate=canlib.canBITRATE_500K,
                       outputControl=canlib.Driver.NORMAL):
        ch = canlib.openChannel(channel, open_flags)
        # print("Using channel: %s, EAN: %s" % (ChannelData(channel).device_name,
        #                                       ChannelData(channel).card_upc_no))
        ch.setBusOutputControl(outputControl)
        ch.setBusParams(bitrate)
        ch.busOn()
        return ch

    @staticmethod
    def tear_down_channel(ch):
        ch.busOff()
        ch.close()

    print("Listening...")
    def rev_data(self):
        ch = self.set_up_channel()

        while True:
            try:
                frame = ch.read()
                print(frame)
            except Exception as e:
                print(e)

        self.tearDownChannel(ch)


    def op_frame(self, frame, db):
        kvadblib.Dbc(filename=self.dbc_file)
        bmsg = db.interpret(frame)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Listen on a CAN channel and print all signals received, as specified by a database.")
    parser.add_argument('channel', type=int, default=1, nargs='?', help=(
        "The channel to listen on."))
    parser.add_argument('--db', default="../dbc/adc_ldc.dbc", help=(
        "The database file to look up messages and signals in."))
    parser.add_argument('--bitrate', '-b', default='250k', help=(
            "Bitrate, one of " + ', '.join(bitrates.keys())))
    parser.add_argument('--ticktime', '-t', type=float, default=0, help=(
        "If greater than zero, display 'tick' every this many seconds"))
    args = parser.parse_args()

    # monitor_channel(args.channel, args.db, bitrates[args.bitrate.upper()], args.ticktime)
