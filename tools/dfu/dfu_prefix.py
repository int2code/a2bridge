import argparse
import zlib

dfu_preamble = 0xA5A5A5A5
dfu_version_tag = 0x01

parser = argparse.ArgumentParser(
                    prog='dfu_prefix',
                    description='Adds int2code specific DFU prefix to raw binary image')

parser.add_argument('-i','--input', required=True, help="Input binary file")

args = parser.parse_args()

def crc32mpeg2(buf, crc=0xffffffff):
    for val in buf:
        crc ^= val << 24
        for _ in range(8):
            crc = crc << 1 if (crc & 0x80000000) == 0 else (crc << 1) ^ 0x104c11db7
    return crc

def add_dfu_prefix(file, len, crc):
    # Create 32B prefix for DFU
    file.write(dfu_preamble.to_bytes(4, 'little'))
    file.write(dfu_version_tag.to_bytes(1, 'little'))
    file.write(len.to_bytes(4, 'little'))
    file.write(crc.to_bytes(4, 'little'))
    reserved = [0] * 19
    file.write(bytes(reserved))

with open(args.input, mode='rb') as bin_file:
    fileContent = bin_file.read()

    with open(args.input + ".dfu", mode= 'wb+') as dfu_file:
        add_dfu_prefix(dfu_file, len(fileContent), crc32mpeg2(fileContent))
        dfu_file.write(fileContent)









