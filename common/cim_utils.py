#!/usr/bin/env python
# -*- coding:utf-8 -*-

import binascii


class Convert:  # 转换
    def __init__(self):
        pass

    @staticmethod
    def str_to_hex_list(data):
        hex_list = []
        temp_str = ""
        a = binascii.hexlify(data)
        for i in range(1, len(a)+1):
            temp_str += a[i-1]
            if i % 2 == 0:
                hex_list.append(temp_str)
                temp_str = ""
        return hex_list

    @staticmethod
    def hex_list_to_str(hex_list):
        hex_data = "".join('%s' % x for x in hex_list)
        return binascii.unhexlify(hex_data)

