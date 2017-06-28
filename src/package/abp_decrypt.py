#! /usr/bin/python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
# Last modified: 2017-06-27 19:08:44

from Crypto.Cipher import AES
import binascii


def convert_bytes_to_str(converted: bytes)->str:
    return bytes(converted).decode('utf-8')


class decodePHYpayload(object):

    def __init__(self, PHYpayload, key):
        """
        name       type
        PHYpayload str
        key        str
        """

        print(PHYpayload)
        self.addr = convert_bytes_to_str(PHYpayload[2:10])
        self.FCnt = convert_bytes_to_str(PHYpayload[12:16])

        self.data = convert_bytes_to_str(PHYpayload[18:-8])
        self.MIC = convert_bytes_to_str(PHYpayload[-8:])

        self.appkey = binascii.unhexlify(key)

        hex_header = '010000000000'
        tail = '00000001'

        self.Ablock = hex_header + self.addr + self.FCnt + tail

    def getdata(self):
        """
        get_data return data(type str)
        """
        en = AES.new(self.appkey, AES.MODE_ECB)
        Ablock = self.Ablock
        print(Ablock)

        hex_Ablock = binascii.unhexlify(Ablock)
        enA = en.encrypt(hex_Ablock)

        hex_data = binascii.unhexlify(self.data)
        b_data = bytearray(hex_data)
        b_enA = bytearray(enA)
        s = ""

        for i in range(len(b_data)):
            s += hex(b_data[i] ^ b_enA[i])[2:]

        return s
