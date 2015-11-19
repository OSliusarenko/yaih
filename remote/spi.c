#define	SCK		BIT5	//P1.5	NRF SCK
#define	MOSI	BIT6	//P1.6	NRF MOSI !!! ?
#define	MISO	BIT7	//P1.7	NRF MISO !!! ?

void SPI_init(void);
unsigned char SPI_txByte(unsigned char byte);


void SPI_init(void)
{
    UCB0CTL1 = UCSWRST; // reset bus
    P1SEL  |= MISO + MOSI + SCK;
  	P1SEL2 |= MISO + MOSI + SCK;

    // 3-pin, 8-bit SPI master
    UCB0CTL0 = UCCKPH + UCMSB + UCMST + UCSYNC;
	UCB0CTL1 |= UCSSEL_2;   // SMCLK
	UCB0BR0 = 0;
	UCB0BR1 = 0;

	UCB0CTL1 &= ~UCSWRST; // unreset bus
};

unsigned char SPI_txByte(unsigned char byte)
{
	UCB0TXBUF = byte & 0xff;
	while (!(IFG2 & UCB0TXIFG));
	return UCB0RXBUF;
}
