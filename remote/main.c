#define BACKLIGHT BIT2
#define BTN_BACK BIT5
#define BTN_OK BIT4
#define BTN_UP BIT0
#define BTN_DOWN BIT1
#define BTN_LEFT BIT3
#define BTN_RIGHT BIT2
#define BUTTONS (BTN_BACK|BTN_OK|BTN_UP|BTN_DOWN|BTN_LEFT|BTN_RIGHT)


volatile unsigned char btn_pressed=0, mint, hrst, hrs_al, min_al, sec_al;
volatile int temperature;
volatile _Bool alarm_set = 0;

void backlightOn();
void backlightOff();
void init();
void initKeyboard();

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

    P1DIR |= LCD5110_SCE_PIN + LCD5110_DC_PIN + BACKLIGHT;
    P1OUT |= LCD5110_SCE_PIN + LCD5110_DC_PIN;

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

void showTime()
{
    writeIntToLCD(hrs);
    writeCharToLCD(':', FNT_NORMAL);
    writeIntToLCD(min);
    writeCharToLCD(':', FNT_NORMAL);
    writeIntToLCD(sec);
    if(NRF_rdOneReg(CONFIG) & CONFIG_PWR_UP) writeCharToLCD('*', FNT_NORMAL);
        else writeCharToLCD('.', FNT_NORMAL);
};

//----------------------------------------------------------------------

void getTemp()
{
    if(ack_pw>3 && RXBuf[0]==0x10 && RXBuf[1]==0xff)
    {
        mint=min; hrst=hrs; // timestamp of temperature reading
        hrs_al=hrs; min_al=min+10; sec_al=sec-2;
        alarm_set = 1;  // alarm clock for next probe
        if(min_al>59)
        {
            min_al -= 60;
            if(++hrs_al>23) hrs_al = 0;
        };

        temperature = ((RXBuf[4]<<8 & 0xFF00) + (RXBuf[5] & 0xFF))*10;
        temperature -= 6464;
        temperature *= 10;
        temperature /= 24;
    };
};

void showTemp()
{
    writeCharToLCD(temperature/100+0x30, FNT_NORMAL);
    writeCharToLCD(temperature/10%10+0x30, FNT_NORMAL);
    writeCharToLCD('.', FNT_NORMAL);
    writeCharToLCD(temperature%10+0x30, FNT_NORMAL);
};

unsigned char isThereTemperatureReady()
{
    if(waitNRF()==0)
    {
        getTemp();
        setAddr(17, 2);
        showTemp();
        NRF_down();
        return 1;
    };

    return 0;
};

//----------------------------------------------------------------------

void main(void) {

    init();

    while(1) // main loop
    {

/*        if (btn_pressed)
        {
            if (btn_pressed==BTN_BACK) LCDoff();
            if (btn_pressed==BTN_OK) LCDon();
            if (btn_pressed==BTN_UP) backlightOn();
            if (btn_pressed==BTN_DOWN) backlightOff();
            btn_pressed=0;
        };
*/
        defaultRX = 1;
        NRF_init(85);

        while(!isThereTemperatureReady())
        {
            setAddr(17, 0);
            showTime();
            delay_sec(1);
        };

        defaultRX = 0;
        NRF_init(86);

        TXBuf[0] = 0x10;
        TXBuf[1] = 0xff;
        TXBuf[2] = RXBuf[2];
        TXBuf[3] = RXBuf[3];
        TXBuf[4] = RXBuf[4];

        NRF_transmit(5);

        NRF_down();

    char i;

    for (i=0; i<9; i++)
    {
        delay_sec(60);
    };
        delay_sec(30);

    };

}
