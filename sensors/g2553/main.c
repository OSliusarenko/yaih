/*
 * main.c
 */


#define defaultRX			0
#define payloadWidth		8
#define myIdHigh			0x10
#define myIdLow				0x01
#define opCode1				0X01

#define status_OK			0X00
#define status_BattLow		0X01

#define	TPWR		BIT0
#define	TPWRPortOUT	P2OUT
#define	TPWRPortDIR	P2DIR

// 1 = 4 sec
#define deepSleepTime				1
#define deepSleepTimeLowBatt		150
#define LowBattADC					0x1c0

unsigned char i;
unsigned char tmp;

#include  "msp430g2553.h"

volatile unsigned int deepSleepCnt, deepSleepTimer;

void deepSleep(unsigned char dsCnt);
void sleepDelay(unsigned int cnt);

#include "etc.c"
//#include "uart.c"
#include "nrf24l01.c"


void main(void) {
	/* inits */
	WDTCTL = WDTPW + WDTHOLD;                 // Stop WDT
    
    NRF_init();
    NRF_down();
    
	while(1)
	{
		IO_init();
//		UART_init();
        
        /*
		termInit();
		i2cReadByte(DS1621_CMD_ACCESSCONFIG);
		while(!(i2cBUF & CONVERSION_DONE))
		{
			sleepDelay(1);
			i2cReadByte(DS1621_CMD_ACCESSCONFIG);
		}
//		hex2uart(i2cBUF>>4);
//		hex2uart(i2cBUF);
//		putChar(':');
		i2cReadWord(DS1621_CMD_ACCESSTEMPERATURE);
		termDown();
        */
         
		P1OUT |=LED0;
		//get voltage
		ADC10CTL1 = INCH_11;                      // AVcc/2
		ADC10CTL0 = SREF_1 + ADC10SHT_2 + REFON + REF2_5V + ADC10ON + ADC10IE;
	    ADC10CTL0 |= ENC + ADC10SC;             // Sampling and conversion start
	    __bis_SR_register(CPUOFF + GIE);        // LPM0, ADC10_ISR will force exit
	    ADC10CTL0=0x0;

		NRF_init();
        
		TXBuf[0]=myIdHigh;
		TXBuf[1]=myIdLow;
		TXBuf[2]=opCode1;
		if (ADC10MEM>LowBattADC)
		{
			TXBuf[3]=status_OK;
		}else{
			TXBuf[3]=status_BattLow;
		}
		TXBuf[4]=0;
		TXBuf[5]=0;
		TXBuf[6]=(ADC10MEM>>8) & 0Xff;
		TXBuf[7]=ADC10MEM & 0Xff;
		NRF_cmd(W_TX_PAYLOAD, payloadWidth);
	    NRF_transmit();

		while(!(NRF_status() & STATUS_TX_DS))	//wait tx
		{
			tmp=NRF_status();
//			putChar(0x0a);
//			putChar(0x0d);
//			hex2uart(tmp>>4);
//			hex2uart(tmp);
		}
		NRF_down();

		P1OUT &=~LED0;
//		putChar(0x0a);
//		putChar(0x0d);
//		tmp=NRF_status();
//		hex2uart(tmp>>4);
//		hex2uart(tmp);
//		putChar('|');

//		hex2uart(i2cWORD>>12);
//		hex2uart(i2cWORD>>8);
//		hex2uart(i2cWORD>>4);
//		hex2uart(i2cWORD);
//	    putChar(':');
//		hex2uart(ADC10MEM>>12);
//		hex2uart(ADC10MEM>>8);
//		hex2uart(ADC10MEM>>4);
//		hex2uart(ADC10MEM);

		//check battery voltage
		if(ADC10MEM>LowBattADC)
		{
			deepSleep(deepSleepTime);
		}else{
			deepSleep(deepSleepTimeLowBatt);
		}

	}
}

/*
 * i2c:
 * mosi(p1.7) = SDA
 * miso(p1.6) = SCK
 * */


//USCIAB RX
void __attribute__ ((interrupt(USCIAB0RX_VECTOR))) USCI0RX_ISR(void)
{
_NOP();
}


void __attribute__ ((interrupt(ADC10_VECTOR))) ADC10_ISR (void)
{
  __bic_SR_register_on_exit(CPUOFF);        // Clear CPUOFF bit from 0(SR)
}


void __attribute__ ((interrupt(WDT_VECTOR))) watchdog_timer (void)
{
	//P1OUT ^=LED0;
	if(++deepSleepCnt > deepSleepTimer)
	{
		_BIC_SR_IRQ(LPM3_bits);                   // Clear LPM3 bits from 0(SR)
	}
}




void deepSleep(unsigned char dsCnt)
{
	ADC10CTL0=0;
	BCSCTL1 |= DIVA_2;                        // ACLK/4
	WDTCTL = WDT_ADLY_1000;                   // WDT 1s/4 interval timer
	P1DIR = 0xFF;                             // All P1.x outputs
	P1OUT = 0;                                // All P1.x reset
	P2DIR = 0xFF;                             // All P2.x outputs
	P2OUT = 0;                                // All P2.x reset
	deepSleepCnt=0;
	deepSleepTimer=dsCnt;
	IE1 = WDTIE;                             // Enable WDT interrupt
	_BIS_SR(LPM3_bits + GIE);               // Enter LPM3
	WDTCTL=0;
}

void sleepDelay(unsigned int cnt)
{
	BCSCTL1 |= DIVA_2;                      // ACLK/4
	WDTCTL = WDT_ADLY_16;                   //
	deepSleepCnt=0;
	deepSleepTimer=cnt;
	IE1 |= WDTIE;                           // Enable WDT interrupt
	_BIS_SR(LPM3_bits + GIE);               // Enter LPM3
	BCSCTL1 &=~DIVA_2;
	IE1 &= ~WDTIE;                          // Enable WDT interrupt
	WDTCTL = WDTPW + WDTHOLD;               // Stop WDT
}


