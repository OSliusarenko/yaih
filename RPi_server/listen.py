from nrf24_BOARD import NRF24
import time
import datetime
import RPi.GPIO as GPIO
import sys
import signal
import requests
import json
import numpy as np
from HD44780_BOARD import HD44780


def strToListOfInt(msg):
    return [ord(c) for c in msg]


def interrupt_signal_handler(ssignal, frame):
    """ Cleans out pins when ^C received"""
    print 'Exitting...\n'
    signal.setitimer(signal.ITIMER_REAL, 0) # ?
    GPIO.cleanup()
    sys.exit()

def italarm_signal_handler(ssignal, stack):
    """ Does repeatedly one action, for clock """
    tnow = datetime.datetime.today()
    msg = '{:%a %d %b %H:%M}'.format(tnow)
    place_text(msg, 1)


def place_text(strings, row):
    """ Wrapper for LCD """
    s_tmp = strings+' '*(16-len(strings))
    if row == 1:
        s_tmp = '\n' + s_tmp
    LCD.message(s_tmp)

pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]

myId = 0x10
remoteId = 0x00
thermoId = 0xff

radio = NRF24()
radio.begin(0, 0, 15)

radio.setRetries(0,0xf)

radio.setPayloadSize(8)
radio.setChannel(85)
radio.setDataRate(NRF24.BR_1MBPS)
radio.setPALevel(NRF24.PA_MAX)
radio.setAutoAck(False);

radio.setAutoAck(True)
radio.enableDynamicPayloads()
radio.enableAckPayload()

radio.openWritingPipe(pipes[0])
radio.openReadingPipe(1, pipes[1])

radio.startListening()
radio.stopListening()

radio.printDetails()

radio.startListening()

c=1

LCD = HD44780()

signal.signal(signal.SIGINT, interrupt_signal_handler)

place_text('temp', 0)
place_text('-= loading =-', 1)

# for clock
signal.signal(signal.SIGALRM, italarm_signal_handler)
signal.setitimer(signal.ITIMER_REAL, 60, 60)
###

with open('sensor_1.dat', 'a') as f:
    while True:
        pipe = [0]
        # wait for incoming packet from transmitter
        while not radio.available(pipe):
            time.sleep(10000/1000000.0)

        recv_buffer = []
        radio.read(recv_buffer, radio.getDynamicPayloadSize())

        if recv_buffer[0]==myId and recv_buffer[1]==thermoId:
            batt_V = ((recv_buffer[6]<<8 & 0xFF00)
                    + (recv_buffer[7] & 0xFF))*2.5*2/1023-0.1
            temperature = ((recv_buffer[4]<<8 & 0xFF00)
                         + (recv_buffer[5] & 0xFF))*1500/1023/3.55-267

            msg = 't= {:.2f} C'.format(temperature)
            place_text(msg, 0)

            batt_V = np.round(batt_V*10)/10
            temperature = np.round(temperature*100)/100

            msg = '{:.1f}'.format(batt_V) + '\t'
            msg = msg + '{:.1f}'.format(temperature)
            msg = msg + '\n'

            tnow = time.localtime()

            print str(tnow.tm_hour) + ':' +\
                  str(tnow.tm_min) + ':' +\
                  str(tnow.tm_sec) +  ' ' + msg,

            f.write(str(time.time()) + '\t' + msg)
            f.flush()

            http_params = {'time': np.round(time.time()),
                           'temp': temperature,
                           'batt': batt_V}
#            try:
#                requests.post("http://134.168.45.2/data",
#                                          data=json.dumps(http_params))
#            except:
#                pass

        if recv_buffer[0]==myId and recv_buffer[1]==remoteId:
            print 'remote'
            if recv_buffer[2]==ord('g') and recv_buffer[3]==ord('t'):
                print 'Sending time...'
                tm = time.localtime(time.time())
                akpl_buf=[tm.tm_hour, tm.tm_min, tm.tm_sec]
                print akpl_buf
                radio.writeAckPayload(0, akpl_buf, len(akpl_buf))


        c = c + 1


