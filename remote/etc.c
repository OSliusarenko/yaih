#define	LED0	BIT0	//P1.0	LED

void IO_init(void);
void delay (unsigned long a);
void delay_10us (unsigned int a);
void delay_sec (unsigned char a);

volatile unsigned char sec=0, min=0, hrs=0, delaysec_cnt=0xff;

void IO_init(void)
{
	/* LED0 */
	P1OUT &= ~LED0;
	P1DIR |= LED0;
}

void delay (unsigned long a)
{
	while(--a > 0);
	{
	_NOP();
	}
}

void delay_10us (unsigned int a)
{
	CCR0 = 10*a;
	TACTL = TASSEL_2 + MC_1;                  // SMCLK, upmode
	CCTL0 = CCIE;                             // CCR0 interrupt enabled
	__bis_SR_register(LPM0_bits + GIE);
}

void delay_sec (unsigned char a)
{
    if (a>60) a = 60;
    delaysec_cnt = sec + a;
    if (delaysec_cnt>59) delaysec_cnt -= 59;
	__bis_SR_register(LPM3_bits + GIE);
}

void __attribute__ ((interrupt(TIMER0_A0_VECTOR))) ta0_isr(void)
{
  TACTL = 0;
  CCTL0 &= ~CCIE;
  LPM0_EXIT; 
}

void __attribute__ ((interrupt(WDT_VECTOR))) watchdog_timer (void)
{                       // clock
    if(++sec > 59)
    {
        sec = 0;
        if(++min > 59)
        {
            min = 0;
            if (++hrs > 23) hrs = 0;
        };
    };
    
    if(sec==delaysec_cnt)
    {
        delaysec_cnt=0xff;

        _BIC_SR_IRQ(LPM3_bits);           // Clear LPM0 bits from 0(SR) 
    };

}

