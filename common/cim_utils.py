#!/usr/bin/env python
# -*- coding:utf-8 -*-

import binascii


class Convert:  # 转换
    def __init__(self):
        self.hexmap = {
            "0000": "0",
            "0001": "1",
            "0010": "2",
            "0011": "3",
            "0100": "4",
            "0101": "5",
            "0110": "6",
            "0111": "7",
            "1000": "8",
            "1001": "9",
            "1010": "A",
            "1011": "B",
            "1100": "C",
            "1101": "D",
            "1110": "E",
            "1111": "F",
        }

    @staticmethod
    def str_to_hex_list(data):
        hex_list = []
        temp_str = ""
        a = binascii.hexlify(data)
        for i in range(1, len(a) + 1):
            temp_str += a[i - 1]
            if i % 2 == 0:
                hex_list.append(temp_str)
                temp_str = ""
        return hex_list

    @staticmethod
    def hex_list_to_str(hex_list):
        hex_data = "".join('%s' % x for x in hex_list)
        return binascii.unhexlify(hex_data)

    @staticmethod
    def str_to_hex(s):
        return ''.join([hex(ord(c)).replace('0x', '') for c in s]).upper()

    @staticmethod
    def getcrc32(filepath):
        file = open(filepath, 'rb')
        return binascii.crc32(file.read())

    def addone(self, mods):
        assert isinstance(mods, list)
        tmods = mods.copy()
        if tmods:
            if tmods[0] == 0:
                tmods[0] = 1
                return (tmods)
            else:
                return ([0] + self.addone(tmods[1:]))
        return ([])

    def convertToBinary(self, num, site=64):
        assert -2 ** (site - 1) <= num < 2 ** (site - 1), "the %d is not in range [%d,%d)" % (
            num, -2 ** (site - 1), 2 ** (site - 1))
        mod = []
        quotient = abs(num)
        if quotient == 0:
            mod = [0]
        else:
            while quotient:
                mod.append(quotient % 2)
                quotient = quotient // 2
        mod += [0] * (site - len(mod) - 1)
        # if negative
        if num < 0:
            # not
            mod = [0 if i else 1 for i in mod]
            # add 1
            mod = self.addone(mod)
            # add sign
            mod += [1]
        else:
            mod += [0]
        return ("".join([str(i) for i in reversed(mod)]))

    def convertToHex(self, code):
        clen = len(code)
        mod = clen % 4
        if mod != 0:
            if code[0] == 0:
                code = "0" * (4 - mod) + code
            else:
                code = "1" * (4 - mod) + code
        out = []
        for i in range(0, len(code), 4):
            out.append(self.hexmap[code[i:i + 4]])
        return ("".join(out))