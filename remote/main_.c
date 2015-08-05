#define BACKLIGHT BIT2
#define defaultRX           1
#define payloadWidth        8
#define myId            0x10
#define thermoId             0xFF

#include "msp430g2553.h"

void main(void) {
    
    unsigned char ack_pw, tmp;
    int i;
    
    WDTCTL = WDTPW + WDTHOLD; // disable WDT
    BCSCTL1 = CALBC1_1MHZ; // 1MHz clock
    DCOCTL = CALDCO_1MHZ;
    
    P1OUT = 0;
    P2OUT = 0;
    P1DIR = 0;
    P2DIR = 0;
    
//    while(1);

    _BIS_SR(LPM3_bits);
        
}
