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

    # def file_reset(self):
    #     srec_file = SRecordFile(self.file_path)
    #     out_file = open(self.out_path, "wb")
    #     print("size:", srec_file.size())
    #     print("lines:", srec_file.lines())
    #     print("mot_type:", srec_file.mot_type())
    #     print("record_counts:", srec_file.record_counts())
    #     print("has_header:", srec_file.has_header())
    #     print("min_address:", srec_file.min_address())
    #     print("max_address:", srec_file.max_address())
    #     print("header_content:", srec_file.header_content())
    #     print("records:", srec_file.records[0].count)
    #
    #     for srec_line in srec_file.records:
    #         line_str = srec_line.build_str()
    #         if not srec_line.is_crc_valid():
    #             line_len = len(line_str)
    #             now_crc = line_str[line_len-2: line_len]
    #             correct_crc = str(struct.pack(">B", srec_line.calc_crc())).upper()[4:6]
    #
    #             line_str = "%s%s" % (line_str[:line_len-2], correct_crc)
    #             print(srec_line, "error crc:", now_crc, "correct crc:", correct_crc)
    #         else:
    #             print(srec_line, "crc correct")
    #             pass
    #
    #         line_str = "%s\r\n" % line_str
    #         out_file.write(line_str.encode("ascii"))
    #
    #     print("Generate binary S-Record file to '%s'" % self.out_path)

    # 生成单起始地址文件
    def generate_srec(self, type, bin_start, read_length, address_start):
        bin_file = open("test.bin", "rb")
        # bin_file = open("same_base.bin", "rb")
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

    # 生成多起始地址文件
    def generate_srec_different(self, type=1, data_list=[]):
        if data_list is not None and len(data_list) > 0:
            bin_file = open("test.bin", "rb")
            # bin_file = open("same_base.bin", "rb")
            cb = bincopy.BinFile()
            sum_length = 0
            sum_data = bytes()
            address_start = data_list[0]['address_start']
            for d in data_list:
                bin_start = d['bin_start']
                read_length = d['read_length']
                address_start = d['address_start']

                sum_length += read_length

                bin_file.seek(bin_start)
                data = bin_file.read(read_length-1) + struct.pack(">B", 2)
                sum_data += data
                cb.add_binary(data, address=address_start)

            out_path = r"D:\lrzsz\srec%s_%s_%s_%08X.srec" \
                       % (type, str(hex(sum_length)), str(hex(address_start)), binascii.crc32(sum_data))
            out_file = open(out_path, "wb")

            if type == 1:
                address_length_bits = 16
            elif type == 2:
                address_length_bits = 24
            else:
                address_length_bits = 32
            out_file.write("S00F000068656C6C6F202020202000003C\r\n".encode())
            out_file.write(cb.as_srec(number_of_data_bytes=24, address_length_bits=address_length_bits).encode())
            out_file.close()
            bin_file.close()
            print("generate srec success -> '%s'" % out_path)

    def compute_crc(self):
        f = bincopy.BinFile()
        f.add_srec_file("D:\lrzsz\IC216.mhx")
        f.fill(value=b'\xff')
        # min = f.minimum_address
        # max = f.maximum_address
        # print(f.as_binary(minimum_address=f.minimum_address, maximum_address=f.maximum_address))
        print("%08X" % binascii.crc32(f.as_binary()))





s = Srec()
s.compute_crc()
# s.generate_srec(type=2, bin_start=0x100, read_length=1024*35, address_start=0x80000)
# s.generate_srec(type=2, bin_start=0x200, read_length=1024*53, address_start=0x80000)
# s.generate_srec(type=2, bin_start=0x400, read_length=1024*320, address_start=0x170000)
# # s.generate_srec(type=2, bin_start=0x500, read_length=1024*58, address_start=0e=2, bin_start=0x300, read_length=1024*77, address_start=0xC0000)
# s.generate_srec(typx1C0000)
# s.generate_srec(type=2, bin_start=0x600, read_length=1024*22, address_start=0x200000)


# data_list = [{'bin_start': 100, 'read_length': 0x04000, 'address_start': 0x00004000},
#              {'bin_start': 600, 'read_length': 0x02000, 'address_start': 0x0000C000},
#              {'bin_start': 200, 'read_length': 0x04000, 'address_start': 0x00088000},
#              {'bin_start': 200, 'read_length': 0x04000, 'address_start': 0x00098000},
#              {'bin_start': 1000, 'read_length': 0x04000, 'address_start': 0x000A8000},
#              {'bin_start': 400, 'read_length': 0x04000, 'address_start': 0x000B8000},
#              {'bin_start': 0, 'read_length': 0x04000, 'address_start': 0x000C8000},
#              {'bin_start': 700, 'read_length': 0x04000, 'address_start': 0x000E8000}]
# s.generate_srec_different(type=2, data_list=data_list)
# w = open("D:\lrzsz\same_base_w.bin", "ab")
# f = open("D:\lrzsz\same_base.bin", "rb")
# data = f.read()
# f.close()
# for i in range(300):
#     # data.append(f.read())
#     # print(f.read())
#     w.write(data)
#
# # w.writelines(data)
# w.close()


