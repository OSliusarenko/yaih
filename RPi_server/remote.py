from nrf24 import NRF24
import time
from mpd import MPDClient
import subprocess


RMT_NOP = 0x00 # wait reply
RMT_TEST = 0x01 # test signal (should receive ack 'ok' after)
RMT_OK = 0x02 # 'ok' response, also end-of-session

RMT_GET_PLAYING = 0x10 # get song info from server 

RMT_BTN_BACK = 0x03
RMT_BTN_OK = 0x04
RMT_BTN_UP = 0x05
RMT_BTN_DOWN = 0x06
RMT_BTN_LEFT = 0x07
RMT_BTN_RIGHT = 0x08


def strToListOfInt(msg):
    return [ord(c) for c in msg]

pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]

myId = 0x10
remoteId = 0x00
thermoId = 0xff

radio = NRF24()
radio.begin(0, 0, 22)

radio.setRetries(0,0xf)

radio.setPayloadSize(32)
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

i=0

mpc = MPDClient(use_unicode=True)
mpc.connect("localhost", 6600)
#mpc.update()

while True:
    pipe = [0]
    # wait for incoming packet from transmitter
    while not radio.available(pipe):
        time.sleep(10000/1000000.0)

    recv_buffer = []
    DPSize = radio.getDynamicPayloadSize()
    radio.read(recv_buffer, DPSize)
    
    if DPSize == 1:
        if recv_buffer[0] == RMT_TEST:
            i+=1
            print i, 'test'
            akpl_buf=[RMT_OK]
            radio.writeAckPayload(0, akpl_buf, len(akpl_buf))
        elif recv_buffer[0] == RMT_NOP:
            pass
        elif recv_buffer[0] == RMT_GET_PLAYING:
            """ Send playing track info to remote control's screen """
            songinfo = mpc.currentsong()
            try:
                titleinfo = songinfo['title']
            except:
                titleinfo = songinfo['file']
            if len(titleinfo)>32:
                titleinfo = titleinfo[:31]
            akpl_buf = [ord(c) for c in list(titleinfo)]
            radio.writeAckPayload(0, akpl_buf, len(akpl_buf))
        elif recv_buffer[0] == RMT_BTN_OK:
            try:
                mpc.play()
            except ConnectionError:
                print 'Connection error! reconnect'
                mpc.connect("localhost", 6600)
                mpc.play()
            akpl_buf=[RMT_OK]
            radio.writeAckPayload(0, akpl_buf, len(akpl_buf))
        elif recv_buffer[0] == RMT_BTN_BACK:
            try:
                mpc.pause()
            except ConnectionError:
                print 'Connection error! reconnect'
                mpc.connect("localhost", 6600)
                mpc.pause()
            akpl_buf=[RMT_OK]
            radio.writeAckPayload(0, akpl_buf, len(akpl_buf))
        elif recv_buffer[0] == RMT_BTN_LEFT:
            try:
                mpc.previous()
            except ConnectionError:
                print 'Connection error! reconnect'
                mpc.connect("localhost", 6600)
                mpc.previous()
            akpl_buf=[RMT_OK]
            radio.writeAckPayload(0, akpl_buf, len(akpl_buf))
        elif recv_buffer[0] == RMT_BTN_RIGHT:
            try:
                mpc.next()
            except ConnectionError:
                print 'Connection error! reconnect'
                mpc.connect("localhost", 6600)
                mpc.next()
            akpl_buf=[RMT_OK]
            radio.writeAckPayload(0, akpl_buf, len(akpl_buf))
        elif recv_buffer[0] == RMT_BTN_UP:
            """ Increase volume """
            subprocess.call(['amixer', '-c', '1', '-q', 
                             'set', 'PCM', '10%+'])
            akpl_buf=[RMT_OK]
            radio.writeAckPayload(0, akpl_buf, len(akpl_buf))
        elif recv_buffer[0] == RMT_BTN_DOWN:
            """ Decrease volume """
            subprocess.call(['amixer', '-c', '1', '-q',
                             'set', 'PCM', '10%-'])
            akpl_buf=[RMT_OK]
            radio.writeAckPayload(0, akpl_buf, len(akpl_buf))
    
