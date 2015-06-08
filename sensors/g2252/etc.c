#define	LED0	BIT0	//P1.0	LED

void IO_init(void);
void delay (unsigned long a);
void delay_10us (unsigned long a);

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

void delay_10us (unsigned long a)
{
	CCR0 = 10*a;
	TACTL = TASSEL_2 + MC_1;                  // SMCLK, upmode
	CCTL0 = CCIE;                             // CCR0 interrupt enabled
	__bis_SR_register(LPM0_bits + GIE);
}

void __attribute__ ((interrupt(TIMER0_A0_VECTOR))) ta0_isr(void)
{
  TACTL = 0;
  CCTL0 &= ~CCIE;
  LPM0_EXIT;
}
