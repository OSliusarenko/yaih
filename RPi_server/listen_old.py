from nrf24_BOARD import NRF24
import time
import datetime
from pyA20.gpio import gpio
from pyA20.gpio import port
import sys
import signal
import requests
import json
import numpy as np


pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]

myId = 0x10
remoteId = 0x00
thermoId = 0xff

radio = NRF24()
cepin = port.PA2
print cepin
radio.begin(1, 0, cepin)

radio.setRetries(0,0xf)

radio.setPayloadSize(8)
radio.setChannel(85)
radio.setDataRate(NRF24.BR_1MBPS)
radio.setPALevel(NRF24.PA_MAX)
radio.setAutoAck(False);

#radio.setAutoAck(True)
radio.enableDynamicPayloads()
#radio.enableAckPayload()

radio.openWritingPipe(pipes[0])
radio.openReadingPipe(1, pipes[1])

radio.startListening()
radio.stopListening()

radio.printDetails()

radio.startListening()

#radio.printDetails()

while True:

    time.sleep(5)

    recv_buffer = []
    if radio.available(): 
    	radio.read(recv_buffer, radio.getDynamicPayloadSize())
        if recv_buffer[0]==myId and recv_buffer[1]==thermoId:
            batt_V = ((recv_buffer[6]<<8 & 0xFF00)
                    + (recv_buffer[7] & 0xFF))*2.5*2/1023-0.1
            temperature = ((recv_buffer[4]<<8 & 0xFF00)
                         + (recv_buffer[5] & 0xFF))*1500/1023/3.55-267
            print('{:.2f}V {:.2f}C'.format(batt_V, temperature))
    	else: 
            print(recv_buffer)

radio.stopListening()




