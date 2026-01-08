import interface_pb2
from cobs import cobs
import struct
import serial
import time

COM_NUM = 'COM65'

def crc32mpeg2(buf, crc=0xffffffff):
    for val in buf:
        crc ^= val << 24
        for _ in range(8):
            crc = crc << 1 if (crc & 0x80000000) == 0 else (crc << 1) ^ 0x104c11db7
    return crc

def serialize_protobuf_message(raw_message):
    data_not_encoded = bytearray()
    data_not_encoded += raw_message.SerializeToString()
    data_not_encoded += (crc32mpeg2(data_not_encoded)).to_bytes(4, byteorder='little')
    data_encoded = bytearray()
    data_encoded += cobs.encode(data_not_encoded)
    data_encoded += (0).to_bytes(1, byteorder='little')
    print("Packet: {}".format(data_encoded.hex()))

    return data_encoded

packet = bytearray()
def deserialize_protobuf_message(data):
    global packet
    packet += data
    len_packet = len(packet)
    if len_packet >= 6 and packet[-1] == 0:
        data_decoded = cobs.decode(packet[0:-1])
        crc_calc = crc32mpeg2(data_decoded[0:-4]).to_bytes(4, byteorder='little')
        crc_msg = packet[-5:-1]
        if(crc_calc == crc_msg):
            message = interface_pb2.ResponsePacket()
            message.ParseFromString(data_decoded[0:-4])
            print(message)


message = interface_pb2.RequestPacket()
#message.info_request.dummy = 1
#message.set_serial_request.serial_number = "072323233"
message.status_request.dummy = 1
#message.i2c_over_distance_request.access_type = 2
#message.i2c_over_distance_request.node = 0

#x = message.i2c_over_distance_request.data.add()
#x.reg = 0x65
#x.value = 0xFE
#x = message.i2c_over_distance_request.data.add()
#x.reg = 0x02
#x.value = 0x00
#x = message.i2c_over_distance_request.data.add()
#x.reg = 0x02
#x.value = 0x00
#x = message.i2c_over_distance_request.data.add()
#x.reg = 0x02
#x.value = 0x00
#x = message.i2c_over_distance_request.data.add()
#x.reg = 0x02
#x.value = 0x00
#x = message.i2c_over_distance_request.data.add()
#x.reg = 0x02
#x.value = 0x00
#message.i2c_over_distance_request.data.extend([x, x])
#message.i2c_over_distance_request.value = 0
#message.i2c_over_a2b_request.peripheral_i2c_addr = 0x22

msg1_packet = serialize_protobuf_message(message)

with serial.Serial(COM_NUM, 115200, timeout=0.1) as s:
    s.write(msg1_packet)
    s.flush()
    while True:
        data = s.read()
        deserialize_protobuf_message(data)
        if (len(data) > 0) and (data[-1] == 0x00):
            break



