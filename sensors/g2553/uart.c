#define	RXD		BIT1	//P1.1	UART MSP_RXD
#define	TXD		BIT2	//P1.2	UART MSP_TXD

void UART_init (void);
void putChar(unsigned char byte);
static void hex2uart(unsigned char n);


void UART_init(void)
{
	UCA0CTL1 = UCSWRST;
	BCSCTL1 = CALBC1_1MHZ;                    // Set DCO
	DCOCTL = CALDCO_1MHZ;
	P1SEL |= RXD + TXD;                     // P1.1 = RXD, P1.2=TXD
	P1SEL2 |= RXD + TXD;
	UCA0CTL1 |= UCSSEL_2;                     // SMCLK
	UCA0BR0 = 8;                              // 1MHz 115200
	UCA0BR1 = 0;                              // 1MHz 115200
	UCA0MCTL = UCBRS2 + UCBRS0;               // Modulation UCBRSx = 5
	UCA0CTL1 &= ~UCSWRST;
	IE2 |= UCA0RXIE;
}


/* áàéò â uart */
void putChar(unsigned char byte)
{
	while(!(IFG2 & UCA0TXIFG));
	UCA0TXBUF = byte & 0xFF;
	while(!(IFG2 & UCA0TXIFG));
}

/* ïóëüíóòü â uart HEX-òèðè÷íûì íèáëîì */
static void hex2uart(unsigned char n) {
	static const char hex[16] = { '0', '1', '2', '3', '4', '5', '6', '7', '8',
			'9', 'A', 'B', 'C', 'D', 'E', 'F' };
	while (!(IFG2&UCA0TXIFG));
	UCA0TXBUF=(hex[n & 15]);
}
