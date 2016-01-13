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
void initKeyboard();
char rmtSendBtn(unsigned char btn);

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


char rmtSendBtn(unsigned char btn){
    unsigned char st, i;

    defaultRX = 0;
    NRF_init();

    NRF_irq_clear_all();
    NRF_broadcast_char(btn); // send the button pressed

    while (1)
    {
        st = waitNRF();

        if(st==1) // we got a reply!
        {
            if(ack_pw==1 && RXBuf[0]==0x0) break; // end-of-session
/*
            // show ack payload on screen

            else if(1)
            {
                clearLCD();
                setAddr(0, 1);
                for(i=0; i<ack_pw; i++)
                    writeCharToLCD(RXBuf[i]);
                NRF_broadcast_char(0x0); // send ok
            };*/
        };

        if(st==2) //sent successfully, no ack yet
        {
            NRF_irq_clear_all();
            NRF_broadcast_char(0x0); // send ok, wait ack
        };

        if (st==3) break; // max_ret

    };

    NRF_down();

    return st;
};

char receiveString(){
    unsigned char st, i, number_of_chunks, chunk;

    defaultRX = 0;
    NRF_init();

    NRF_irq_clear_all();
    NRF_broadcast_char(0x5); // send 'want string'

    clearLCD();
    setAddr(0, 0);

// get number of chunks the string will be divided into
    while (1)
    {
        st = waitNRF();

        if(st==1 && ack_pw==1) // we got a reply!
        {
            number_of_chunks=RXBuf[i];
            break; // end-of-session
        };

        if(st==2) //sent successfully, no ack yet
        {
            NRF_irq_clear_all();
            NRF_broadcast_char(0x1); // send 'waiting'
        };

//        if (st==3) break; // max_ret
    };

    while(number_of_chunks--)
    {
        NRF_irq_clear_all();
        NRF_broadcast_char(0x0); // send 'cont'

        // get string
            while (1)
            {
                st = waitNRF();

                if(st==1) // we got a reply!
                {
                    for(i=0; i<ack_pw; i++)
                        writeCharToLCD(RXBuf[i]);
        //            NRF_broadcast_char(0x0);  // send 'success'
                    break; // end-of-session
                };

                if(st==2) //sent successfully, no ack yet
                {
                    NRF_irq_clear_all();
                    NRF_broadcast_char(0x1); // send 'waiting'
                };

        //        if (st==3) break; // max_ret
            };
    };



    NRF_down();

    return st;
};


void main(void) {


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
    NRF_init();
    NRF_down();

    initKeyboard();
    // end init

    writeStringToLCD("hello");

    receiveString();

    while(1)
    {
        delay_sec(1);
    };
/*
    while(1) // main loop
    {
        if (btn_pressed)
        {
            setAddr(0,0);
            switch(RXBuf[0])
            {
                case BTN_BACK:
                    writeStringToLCD("back ");
                    break;
                case BTN_OK:
                    writeStringToLCD("OK   ");
                    rmtSendBtn(BTN_OK);
                    break;
                case BTN_LEFT:
                    writeStringToLCD("left ");
                    break;
                case BTN_RIGHT:
                    writeStringToLCD("right");
                    break;
                case BTN_UP:
                    writeStringToLCD("up   ");
                    break;
                case BTN_DOWN:
                    writeStringToLCD("down ");
                    break;
                default:
                    break;
            };
            btn_pressed=0;
        };

        delay_sec(1);
    };
*/

}
