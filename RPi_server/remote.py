from nrf24 import NRF24
import time

RMT_NOP = 0x00 # wait reply
RMT_TEST = 0x01 # test signal (should receive ack 'ok' after)
RMT_OK = 0x02 # 'ok' response, also end-of-session

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
#            print 'nop'
            pass
    
