from nrf24 import NRF24
import time

pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]

radio = NRF24()
radio.begin(0, 0, 17)

radio.setRetries(0,3)

radio.setPayloadSize(8)
radio.setChannel(0x02)
radio.setDataRate(NRF24.BR_1MBPS)
radio.setPALevel(NRF24.PA_MAX)
radio.setAutoAck(False);

#radio.setAutoAck(True)
#radio.enableDynamicPayloads()
#radio.enableAckPayload()

radio.openWritingPipe(pipes[0])
radio.openReadingPipe(1, pipes[1])

radio.startListening()
radio.stopListening()

radio.printDetails()

radio.startListening()

c=1
while True:
    akpl_buf = [c,1]
    pipe = [0]
    # wait for incoming packet from transmitter
    while not radio.available(pipe):
        time.sleep(10000/1000000.0)

    recv_buffer = []
    radio.read(recv_buffer, radio.getDynamicPayloadSize())
    msg = ''
    if recv_buffer[0] == 0x10:
        msg = msg + 'sensor_1: '
    if recv_buffer[3] == 0x0:
        msg = msg + 'battOK, '
    else:
        msg = msg + 'LOWbatt, '

    batt_V = ((recv_buffer[6]<<8 & 0xFF00) + (recv_buffer[7] & 0xFF))* \
             2.5*2/1023

    msg = msg + '{:f}'.format(batt_V)[:5] + 'V'
    print msg
    c = c + 1
    if (c&1) == 0:    # queue a return payload every alternate time
        radio.writeAckPayload(1, akpl_buf, len(akpl_buf))


