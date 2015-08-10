#define BACKLIGHT BIT2

#define payloadWidth        8
#define myId            0x10
#define remoteId        0x00
#define thermoId             0xFF

void backlightOn();
void backlightOff();
void syncTime();
void showTime();
void getTemp();
void showTemp();
char waitNRF();
void isThereTemperatureReady();

volatile unsigned char ack_pw;
volatile unsigned char sec_al=0, min_al=0, hrs_al=0, mint, hrst;
volatile int temperature;
volatile _Bool defaultRX, alarm_set=0;

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
    
    NRF_transmit();

    NRF_down();
    delay_sec(1); 
    NRF_up();     
    NRF_transmit();
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
        setAddr(0, 1);
        showTemp();
        NRF_down();
    };
};

char waitNRF()
{
    unsigned char tmp=NRF_status();
      
    if(tmp & STATUS_RX_DR)
    {
        TXBuf[0] = 0xFF; // NRF's NOP
        NRF_cmd(0x60, 1); // get dyn payload width
        ack_pw = RXBuf[0];
        NRF_readRX(ack_pw);
        
        NRF_flush_rx();
        if(defaultRX) return 1;
    }    
    if(tmp & STATUS_TX_DS)
    {
        NRF_flush_tx();
        return 2;
    }
    if(tmp & STATUS_MAX_RT)
    {
        clearBank(1);
        writeStringToLCD("max_ret");
        NRF_flush_tx();
        NRF_flush_rx();
        return 3;
    }
    return 0;
};

void main(void) {
    
    unsigned char ci;
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
    NRF_down(); // end init

    syncTime(); //getting time
    hrs=RXBuf[0]; min=RXBuf[1]; sec=RXBuf[2];

    defaultRX = 1;
    NRF_init(); // start listening for temperature info
    
    while(1)
    {   
        setAddr(0, 0);
        showTime();
        
        if(alarm_set)
        {
            if(hrs==hrs_al && min==min_al && sec==sec_al)
            {
                defaultRX = 1;
                NRF_init(); // start listening again
                alarm_set = 0;
            };
        }else
        {
            isThereTemperatureReady();
        };

        delay_sec(1);
    };

}
