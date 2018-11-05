#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
from canlib import canlib, kvadblib



# if __name__ == '__main__':
#     parser = argparse.ArgumentParser(
#         description="Listen on a CAN channel and print all signals received, as specified by a database.")
#     parser.add_argument('channel', type=int, default=1, nargs='?', help=(
#         "The channel to listen on."))
#     parser.add_argument('--db', default="engine_example.dbc", help=(
#         "The database file to look up messages and signals in."))
#     parser.add_argument('--bitrate', '-b', default='500k', help=(
#             "Bitrate, one of " + ', '.join(bitrates.keys())))
#     parser.add_argument('--ticktime', '-t', type=float, default=0, help=(
#         "If greater than zero, display 'tick' every this many seconds"))
#     args = parser.parse_args()
#
#     monitor_channel(args.channel, args.db, bitrates[args.bitrate.upper()], args.ticktime)
