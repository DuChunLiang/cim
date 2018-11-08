#!/usr/bin/env python
# -*- coding:utf-8 -*-

import struct
import random
import bincopy
import binascii
from zwuenf.pysrec.SRecordFile import SRecord
from zwuenf.pysrec.SRecordFile import SRecordFile, MOTType


class Srec:

    def __init__(self):
        self.path = "D:\lrzsz"
        self.file_name = "IC218V1_0.srec"
        self.out_name = "srec_test_out.srec"
        self.file_path = "%s\%s" % (self.path, self.file_name)
        self.out_path = "%s\%s" % (self.path, self.out_name)
        self.base64_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']

    def file_reset(self):
        srec_file = SRecordFile(self.file_path)
        out_file = open(self.out_path, "wb")
        print("size:", srec_file.size())
        print("lines:", srec_file.lines())
        print("mot_type:", srec_file.mot_type())
        print("record_counts:", srec_file.record_counts())
        print("has_header:", srec_file.has_header())
        print("min_address:", srec_file.min_address())
        print("max_address:", srec_file.max_address())
        print("header_content:", srec_file.header_content())
        print("records:", srec_file.records[0].count)

        for srec_line in srec_file.records:
            line_str = srec_line.build_str()
            if not srec_line.is_crc_valid():
                line_len = len(line_str)
                now_crc = line_str[line_len-2: line_len]
                correct_crc = str(struct.pack(">B", srec_line.calc_crc())).upper()[4:6]

                line_str = "%s%s" % (line_str[:line_len-2], correct_crc)
                print(srec_line, "error crc:", now_crc, "correct crc:", correct_crc)
            else:
                print(srec_line, "crc correct")
                pass

            line_str = "%s\r\n" % line_str
            out_file.write(line_str.encode("ascii"))

        print("Generate binary S-Record file to '%s'" % self.out_path)

    def generate_srec(self, type, bin_start, read_length, address_start):
        # bin_file = open("test_1.bin", "rb")
        bin_file = open("same_base.bin", "rb")
        bin_file.seek(bin_start)
        data = bin_file.read(read_length-1) + struct.pack(">B", 2)
        # print(data)
        f = bincopy.BinFile()
        f.add_binary(data, address=address_start)

        out_path = r"D:\lrzsz\srec%s_%s_%s_%08X.srec" \
                   % (type, str(hex(read_length)), str(hex(address_start)), binascii.crc32(data))
        out_file = open(out_path, "wb")

        if type == 1:
            address_length_bits = 16
        elif type == 2:
            address_length_bits = 24
        else:
            address_length_bits = 32

        out_file.write("S00F000068656C6C6F202020202000003C\r\n".encode())
        out_file.write(f.as_srec(number_of_data_bytes=24, address_length_bits=address_length_bits).encode())
        out_file.close()
        bin_file.close()
        print("generate srec success -> '%s'" % out_path)


    def create_random_data(self, count):
        hexstring = ""
        for i in range(count):
            base64_str = "%s%s" % (self.base64_list[random.randint(0, 15)], self.base64_list[random.randint(0, 15)])
            if random.randint(0, 1) == 1:
                base64_str = "ff"
            hexstring += base64_str

        return list(bytearray.fromhex(hexstring.upper()))

    def generate_random_srec(self):
        srec_file = SRecordFile(self.file_path)
        out_file = open(self.out_path, "wb")
        # print("size:", srec_file.size())
        # print("lines:", srec_file.lines())
        # print("mot_type:", srec_file.mot_type())
        # print("record_counts:", srec_file.record_counts())
        # print("has_header:", srec_file.has_header())
        # print("min_address:", srec_file.min_address())
        # print("max_address:", srec_file.max_address())
        # print("header_content:", srec_file.header_content())
        print("records:", srec_file.records[srec_file.lines()-1].count)
        address_start = 10240
        max_line = 10643
        srec_count = random.randint(1000, 10643)
        count = 0
        for line in srec_file.records:
            count += 1
            if count == 1:
                print(line)
                out_file.write(line.build_str())
            elif count < srec_count:
                if line.type == 2:
                    line.address = address_start
                    address_start += len(line.data)
                    line.data = self.create_random_data(16)
                    print(line)
            # else:
            #     break

        print(srec_file.records[srec_file.lines()-1])
        # print("Generate binary S-Record file to '%s'" % self.out_path)


s = Srec()
s.generate_srec(type=2, bin_start=0x200, read_length=0x3000, address_start=0x5000)
# s.generate_srec(type=2, bin_start=0x300, read_length=0x04000, address_start=0x00098000)
# s.generate_srec(type=2, bin_start=0x400, read_length=0x04000, address_start=0x000A8000)
# s.generate_srec(type=2, bin_start=0x500, read_length=0x04000, address_start=0x000B8000)
# s.generate_srec(type=2, bin_start=0x600, read_length=0x04000, address_start=0x000C8000)
# s.generate_srec(type=2, bin_start=0x700, read_length=0x04000, address_start=0x00004000)
# s.generate_srec(type=2, bin_start=0x800, read_length=0x04000, address_start=0x000E8000)

# print(s.create_random_data(15))

# file = open("D:\lrzsz\same_base.bin", "wb+")
# for i in range(100000):
#     file.write(struct.pack(">B", 1))
# file.close()
#
# file = open("D:\lrzsz\same_base.bin", "rb")
# print(file.read())
# file.close()

# print(binascii.crc32(b"\x01\x00\x00\x00\x00\x10\x67\x00\x00\x00"))
