from nrf24 import NRF24
import time

def strToListOfInt(msg):
    return [ord(c) for c in msg]

pipes = [[0xe7, 0xe7, 0xe7, 0xe7, 0xe7], [0xc2, 0xc2, 0xc2, 0xc2, 0xc2]]

radio = NRF24()
radio.begin(0, 0, 17)

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

akpl_buf= strToListOfInt('Hello my dear! I\'ve got something for you')

with open('sensor_1.dat', 'a') as f:
    while True:
        pipe = [0]
        # wait for incoming packet from transmitter
        while not radio.available(pipe):
            time.sleep(10000/1000000.0)

        recv_buffer = []
        radio.read(recv_buffer, radio.getDynamicPayloadSize())
        msg = ''

        if recv_buffer[0]==0x10 and recv_buffer[1]==0xFF:   
            batt_V = ((recv_buffer[6]<<8 & 0xFF00) 
                    + (recv_buffer[7] & 0xFF))
            temperature = ((recv_buffer[4]<<8 & 0xFF00) 
                         + (recv_buffer[5] & 0xFF))

            msg = msg + '{:.3f}'.format(batt_V*2.5*2/1023-0.1) + '\t'
            msg = msg + '{:.3f}'.format(temperature*1500/1023/3.55-267)
            msg = msg + '\n'
          
            tnow = time.localtime()
            print str(tnow.tm_hour) + ':' +\
                  str(tnow.tm_min) + ':' +\
                  str(tnow.tm_sec) +  ' ' + msg,

            f.write(str(time.time()) + '\t' + msg)
            f.flush()	

        if recv_buffer[0]==0x10 and recv_buffer[1]==0x00:   
            msg = msg + str(recv_buffer[3])
            msg = msg + '\n'
          
            print msg,

        c = c + 1
        radio.writeAckPayload(0, akpl_buf, len(akpl_buf))


