#define BACKLIGHT BIT2
#define BUTTONS (BIT0|BIT1|BIT2|BIT3|BIT4|BIT5)
#define BTN_BACK 5
#define BTN_OK 4
#define BTN_UP 0
#define BTN_DOWN 1
#define BTN_LEFT 3
#define BTN_RIGHT 2

#define RMT_NOP 0x00 // wait reply
#define RMT_TEST 0x01 // test signal (should receive ack 'ok' after)
#define RMT_OK 0x02 // 'ok' response, also end-of-session
#define RMT_GET_PLAYING 0x10 // get song info from server 
#define RMT_BTN_BACK 0x03
#define RMT_BTN_OK 0x04
#define RMT_BTN_UP 0x05
#define RMT_BTN_DOWN 0x06
#define RMT_BTN_LEFT 0x07
#define RMT_BTN_RIGHT 0x08



#define myId            0x10
#define remoteId        0x00
#define thermoId             0xFF

void backlightOn();
void backlightOff();
void syncTime();
void showTime();
void getTemp();
void showTemp();
void isThereTemperatureReady();
void initKeyboard();
char rmtSendComm(unsigned char comm);

volatile unsigned char temp_timer, btn_pressed=0xf;
volatile unsigned char sec_al=0, min_al=0, hrs_al=0, mint, hrst;
volatile int temperature;
volatile _Bool defaultRX, alarm_set=0, show_mode=1, backlight=0;
volatile _Bool playmode=0;

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

void syncTime()
{
    defaultRX = 0;
    NRF_init();       
    
    TXBuf[0]=myId;
    TXBuf[1]=remoteId;
    TXBuf[2]='g';
    TXBuf[3]='t';
    
    NRF_transmit(4);

    NRF_down();
    delay_sec(1); 
    NRF_up();     
    NRF_transmit(4);
    NRF_down();
};

void showTime()
{
    writeIntToLCD(hrs);
    writeCharToLCD(':');
    writeIntToLCD(min);
    writeCharToLCD(':');
    writeIntToLCD(sec);
    if(NRF_rdOneReg(CONFIG) & CONFIG_PWR_UP) writeCharToLCD('*');
        else writeCharToLCD(' ');
};

void getTemp()
{
    if(ack_pw>3 && RXBuf[0]==myId && RXBuf[1]==thermoId)
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
    writeCharToLCD(temperature/100+0x30);
    writeCharToLCD(temperature/10%10+0x30);
    writeCharToLCD('.');
    writeCharToLCD(temperature%10+0x30);
    writeStringToLCD(" at ");
    writeIntToLCD(hrst);
    writeCharToLCD(':');
    writeIntToLCD(mint);
};

void isThereTemperatureReady()
{
    if(waitNRF()==1)
    {
        getTemp();
        if(show_mode)
        {
            setAddr(0, 1);
            showTemp();
        };
        NRF_down();
    };
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
    switch(P2IFG & BUTTONS)
    {
        case BIT0:
          P2IFG &= ~BIT0;
          btn_pressed = 0;
          break;
        
        case BIT1:
          P2IFG &= ~BIT1;
          btn_pressed = 1;
          break;

        case BIT2:
          P2IFG &= ~BIT2;
          btn_pressed = 2;
          break;

        case BIT3:
          P2IFG &= ~BIT3;
          btn_pressed = 3;
          break;
        
        case BIT4:
          P2IFG &= ~BIT4;
          btn_pressed = 4;
          break;

        case BIT5:
          P2IFG &= ~BIT5;
          btn_pressed = 5;
          break;
        
        default:
          P2IFG = 0;
          return;
    }
} //P2_ISR

char rmtSendComm(unsigned char comm){
    unsigned char st, i;
    
    defaultRX = 0;  
    NRF_init();  
    
    NRF_irq_clear_all();
    NRF_broadcast_char(comm); // send command
    while (1)
    {
        st = waitNRF(); 
        if(st==1) // we got a reply!
        {
            if(ack_pw==1 && RXBuf[0]==RMT_OK) break; // end-of-session
            // show ack payload on screen
            else if(show_mode) 
            {
                clearLCD();
                setAddr(0, 1);
                for(i=0; i<ack_pw; i++)
                    writeCharToLCD(RXBuf[i]);
                
                break; //!!!
            };
        };
        if(st==2) //sent successfully, no ack yet
        {
            NRF_irq_clear_all();
            NRF_broadcast_char(RMT_NOP); // send nop, wait ack
        };
        if (st==3) break;
    };     
    
    NRF_down(); 
    
    return st;
};




void main(void) {
    

    int i;
        
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

    //syncTime(); //getting time
    //hrs=RXBuf[0]; min=RXBuf[1]; sec=RXBuf[2];

    while(1) // main loop
    {
        if(btn_pressed!=0xf) {
            if(btn_pressed==BTN_BACK)
            {
                rmtSendComm(RMT_BTN_BACK);
                playmode = 0;
            };
            if(btn_pressed==BTN_OK)
            {
                rmtSendComm(RMT_BTN_OK);
                playmode = 1;
            };
            if(btn_pressed==BTN_LEFT)
            {
                rmtSendComm(RMT_BTN_LEFT);
            };
            if(btn_pressed==BTN_RIGHT)
            {
                rmtSendComm(RMT_BTN_RIGHT);
            };
            if(btn_pressed==BTN_UP)
            {
                rmtSendComm(RMT_BTN_UP);
            };
            if(btn_pressed==BTN_DOWN)
            {
                rmtSendComm(RMT_BTN_DOWN);
            };
/*            if(btn_pressed==BTN_OK)
            {
                show_mode = !show_mode;
                if(show_mode) 
                {
                    initLCD();
                }
                else LCDoff();
            };
*/

            btn_pressed = 0xf;
        };
        
/*        if(show_mode) 
        {
            setAddr(0, 0);
            showTime();
        };
*/        
        if (playmode) rmtSendComm(RMT_GET_PLAYING);   
        
        delay_sec(1);
        
        
    };

}
