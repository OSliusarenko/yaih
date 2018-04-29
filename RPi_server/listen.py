import datetime
import time
import argparse
from influxdb import InfluxDBClient

from nrf24_BOARD import NRF24
from pyA20.gpio import gpio
from pyA20.gpio import port

import numpy as np

import io
from PIL import Image, ImageDraw, ImageFont


def txt2strpic(txt, image, font, size, conv_to_char=True):
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font, size)

    draw.text((10, 0), txt, fill=1, font=font)

    output = io.BytesIO()

    image.save(output, format="XBM")
    out = output.getvalue()
    res = out.split('{')[1].split('}')[0].split(',')

    mystr = ''

    k = 0
    for s in res:
        k += 1
        if k == 11:
            k = 0
            mystr += '{:08b}'.format(int(s, 16))[:4][::-1]
        else:
            mystr += '{:08b}'.format(int(s.strip(), 16))[::-1]

    if conv_to_char:
        res = [mystr[i:i+8] for i in xrange(0, len(mystr), 8)]
        mystr = ''
        for b in res:
            mystr += chr(int(b, 2))
        mystr = [mystr[i:i+24] for i in xrange(0, len(mystr), 24)]

    return mystr


class InfluxDB(object):
    def __init__(self):
        """Establish a connection to the InfluxDB."""
        self.connect()

    def connect(self):
        self.client = InfluxDBClient(host='127.0.0.1', port=8086,
                                     username='root', password='secret',
                                     database='mydb')

    def send_data(self, json_body):
        self.client.write_points(json_body)

    def close(self):
        self.client.close()


class Sensor(object):
    def __init__(self, sensor_name, measurement_name, index_name):
        self.sensor_name = sensor_name
        self.measurement_name = measurement_name
        self.index_name = index_name

    def create_json(self, value):
        epoch = int(time.time())*1000000000
        return [{
                "measurement": self.measurement_name,
                "tags": {
                    "sensor": self.sensor_name,
                    "index": self.index_name
                },
                "time": epoch,
                "fields": {
                    "value": value
                }
                }]


class NRF24L01(object):
    def __init__(self):
        pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7],
                     [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]

        self.myId = 0x10
        self.remoteId = 0x00
        self.thermoId = 0xff

        self.radio = NRF24()
        cepin = port.PA2
        self.radio.begin(1, 0, cepin)

        self.radio.setRetries(0,0xf)

        self.radio.setPayloadSize(8)
        self.radio.setChannel(85)
        self.radio.setDataRate(NRF24.BR_1MBPS)
        self.radio.setPALevel(NRF24.PA_MAX)
        self.radio.setAutoAck(True);

        self.radio.enableDynamicPayloads()
        #radio.enableAckPayload()

        self.radio.openWritingPipe(pipes[0])
        self.radio.openReadingPipe(1, pipes[1])

        self.radio.startListening()
        self.radio.stopListening()

        self.radio.printDetails()

        self.radio.startListening()

    def packet_available(self):
        return self.radio.available()

    def packet_read(self):
        recv_buffer = []
        myDevices = [self.thermoId, self.remoteId]
        payload_size = self.radio.getDynamicPayloadSize()
        self.radio.read(recv_buffer, payload_size)
        if payload_size > 2:
            if recv_buffer[0] == self.myId:
                try:
                    idx = myDevices.index(recv_buffer[1])
                    return ['thermo', 'remote'][idx], recv_buffer[2:]
                except ValueError:
                    print('Packet from unknown device received')
            else:
                print('Unknown packet received')
        return 'unknown', recv_buffer

    def stop(self):
        self.radio.stopListening()

    def transmit(self, packet):
        self.radio.write(packet)


if __name__ == '__main__':

    def send_response_to_remote(chunk, response):
        packet = str(chr(gate.myId)) + str(chr(chunk)) + response + str(chr(0x00))
        gate.transmit(packet)

    def wait_response_from_remote():
        if gate.packet_available():
            who_sent, packet = gate.packet_read()
            if who_sent == 'remote':
                return int(packet[0])
        else:
            return -1


    gate = NRF24L01()
    db = InfluxDB()

    # define sensors
    outer_temp = Sensor("my_outdoor_sensor", "esp8266", 'street_temperatue')
    outer_batt = Sensor("my_outdoor_sensor", "esp8266", 'battery_voltage')
    batt = 0; temp = 0

    mystr = txt2strpic('Hola!', Image.new("1", (84,48), color=0),
                       'Times_New_Roman_Bold.ttf', 25)


    while True:
        time.sleep(0.1)

        if gate.packet_available():
            who_sent, packet = gate.packet_read()
            print('Packet from {:} received: {:}'.format(who_sent, packet))

            if who_sent == 'thermo':
                batt = ((packet[4]<<8 & 0xFF00)
                        + (packet[5] & 0xFF))*2.5*2/1023-0.1
                temp = ((packet[2]<<8 & 0xFF00)
                        + (packet[3] & 0xFF))*1500/1023/3.55-267

                print('{:.2f}V {:.2f}C'.format(batt, temp))
                db.send_data(outer_temp.create_json(temp))
                db.send_data(outer_batt.create_json(batt))

            elif who_sent == 'remote':
                r =  [0xFF, 0x00, 0xFF, 0x00, 0xFF,
                      0x00, 0x00, 0x00, 0x00, 0x00,
                      0x00, 0x00, 0x00, 0x00, 0x00,
                      0x00, 0x00, 0x00, 0x00, 0x00,
                      0x00, 0x00, 0x00, 0x00]
#                r = np.random.randint(0xFF, size=24)

                gate.radio.stopListening()
                for h in xrange(1):
                    print('Attempt {:}'.format(h))
                    for chunk in xrange(21):
                        send_response_to_remote(chunk, ''.join(map(chr, r)))
#                        send_response_to_remote(chunk, mystr[chunk])
#                        print(mystr[chunk])
                        time.sleep(0.005)
                gate.radio.startListening()





