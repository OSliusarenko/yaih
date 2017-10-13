#define BACKLIGHT BIT2
#define BTN_BACK BIT5
#define BTN_OK BIT4
#define BTN_UP BIT0
#define BTN_DOWN BIT1
#define BTN_LEFT BIT3
#define BTN_RIGHT BIT2
#define BUTTONS (BTN_BACK|BTN_OK|BTN_UP|BTN_DOWN|BTN_LEFT|BTN_RIGHT)


volatile unsigned char btn_pressed=0;

void backlightOn();
void backlightOff();
void init();
void initKeyboard();
char receiveString(unsigned char cmd);

#include "msp430g2553.h"
#include "PCD8544.c"
#include "etc.c"
#include "nrf24l01.c"

void backlightOn()
{
    P1OUT |= BACKLIGHT;
}

void backlightOff()
{
    P1OUT &= ~BACKLIGHT;
}

void init()
{
    WDTCTL = WDTPW + WDTHOLD; // disable WDT
    BCSCTL1 = CALBC1_1MHZ; // 1MHz clock
    DCOCTL = CALDCO_1MHZ;

    P1OUT = 0;
    P2OUT = 0;
    P1DIR = 0;
    P2DIR = 0;

    WDTCTL = WDT_ADLY_1000;                   // WDT 1s interval timer
    IE1 = WDTIE;                             // Enable WDT interrupt

    P1OUT |= LCD5110_SCE_PIN + LCD5110_DC_PIN;
    P1DIR |= LCD5110_SCE_PIN + LCD5110_DC_PIN + BACKLIGHT;

    SPI_init();
    __delay_cycles(50000);
    initLCD();
    clearLCD();

    defaultRX = 0;
    NRF_init(86);
    NRF_down();

    initKeyboard();
    // end init
};

void initKeyboard()
{
    P2OUT = 0;
    P2REN = BUTTONS; // pull-up resistors on
    P2OUT = BUTTONS; // pull-up the buttons
    P2IES = BUTTONS; // define interrupt 1->0
    P2IFG = 0;
    P2IE  = BUTTONS; // enable interrupts
};

// Buttons interrupt service routine
#if defined(__TI_COMPILER_VERSION__) || defined(__IAR_SYSTEMS_ICC__)
#pragma vector=PORT2_VECTOR
__interrupt void P2_ISR(void)
#elif defined(__GNUC__)
void __attribute__ ((interrupt(PORT2_VECTOR))) P2_ISR (void)
#else
#error Compiler not supported!
#endif
{
    btn_pressed = (P2IFG & BUTTONS);
    P2IFG = 0;
    return;
} //P2_ISR

char receiveString(unsigned char cmd){
    unsigned char i, x, y, number_of_chunks=0;
    char st;

    defaultRX = 0;
    NRF_init(86);

    NRF_irq_clear_all();
    NRF_broadcast_char(cmd); // send 'want string'

// get number of chunks the string will be divided into and coordinates
    while (1)
    {
        st = waitNRF();

        if(st==0) // we got a reply!
        {
            number_of_chunks=RXBuf[0];
            x = RXBuf[1]; y = RXBuf[2];
            break; // end-of-session
        };

        if(st==1) //sent successfully, no ack yet
        {
            NRF_broadcast_char(0x3); // send 'waiting'
        };

        if (st==-1) break; // max_ret
    };

    setAddr(x, y);

    while(number_of_chunks--)
    {
        NRF_broadcast_char(0x0); // send 'cont'

        // get string
            while (1)
            {
                st = waitNRF();

                if(st==0) // we got a reply!
                {
                    for(i=0; i<ack_pw; i++)
                        writeCharToLCD(RXBuf[i], FNT_NORMAL);
                    break; // end-of-session
                };

                if(st==1) //sent successfully, no ack yet
                {
                    NRF_broadcast_char(0x3); // send 'waiting'
                };

                if (st==-1) break; // max_ret
            };
    };



    NRF_down();

    return st;
};


void main(void) {

    init();
    writeStringToLCD("remote ", FNT_NORMAL);
    writeStringToLCD("test", FNT_INVERTED);
    writeStringToLCD(" ver.", FNT_NORMAL);
    char testBlock[8] = {0x01, 0xFF, 0x00, 0xFF, 0x00, 0xFF, 0x00, 0xFF};

    while(1) // main loop
    {
        if (btn_pressed)
        {
            if(receiveString(btn_pressed)==-1)
            {
                clearLCD();
                writeStringToLCD("failed to connect", FNT_NORMAL);
            };
            btn_pressed=0;
            clearBank(3);
            writeGraphicToLCD(testBlock, 8);
        };

        delay_sec(1);
    };

}
