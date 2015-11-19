/*	i2c	defines	*/
#define 	RXed			BIT0	// áûë ïðèåì áàéòà i2c
#define 	i2cTX			BIT1	// æäåì ïåðåäà÷è i2c

#define	i2cPortOUT	P1OUT
#define	i2cPortDIR	P1DIR
#define	i2cPortSEL	P1SEL
#define	i2cPortSEL2	P1SEL2
#define	i2cPortREN	P1REN
#define	i2cSDA		BIT7
#define	i2cSCK		BIT6

static void i2cReadByte(unsigned char addr);
void i2cReadWord(unsigned char addr);
void i2cSendByte(unsigned char addr,unsigned char byte);
void i2cSendCmd(unsigned char cmd);

volatile unsigned int  	FLAGS;
volatile unsigned char 	i2cBUF;
volatile unsigned int 	i2cWORD,

void __attribute__ ((interrupt(USCIAB0TX_VECTOR))) USCIAB0TX_ISR(void)
{
	if (FLAGS & i2cTX)
	{
		UCB0TXBUF=i2cBUF;
		__bic_SR_register_on_exit(CPUOFF);

	}else{
		if (!(FLAGS & RXed))
		{
			i2cBUF=UCB0RXBUF;
			FLAGS |= RXed;
			UCB0CTL1 |= UCTXSTP;
			IFG2 &= ~UCB0TXIFG;
			__bic_SR_register_on_exit(CPUOFF);
		}else{
			//i2cBUF=UCB0RXBUF;
			i2cWORD|=UCB0RXBUF;
			IFG2 &= ~UCB0RXIFG;
		}
	}
}

// ÷èòàåì áàéò èç i2c èç àäðåñà addr
static void i2cReadByte(unsigned char addr)
{
	while (UCB0CTL1 & UCTXSTP);
	UCB0CTL1 = UCSWRST;                     		//Enable SW reset
	UCB0CTL0 = UCMST + UCMODE_3 + UCSYNC;         	//I2C Master, synchronous mode
	UCB0CTL1 = UCSSEL_2 + UCSWRST;               	//Use SMCLK, keep SW reset
	UCB0BR0 = 12;                           		//fSCL = SMCLK/12 = ~100kHz
	UCB0BR1 = 0;
	UCB0I2CSA = Ti2cAddr;                     		//Slave Address
	UCB0CTL1 &= ~UCSWRST;                     		//Clear SW reset, resume operation
	IE2 |= UCB0TXIE;                        		//Enable TX interrupt
	IE2 &= ~UCB0RXIE;                        		//Enable RX interrupt
	FLAGS |=i2cTX;
	i2cBUF=addr;
	//P1OUT|=LED0;
	UCB0CTL1 |= UCTR + UCTXSTT;						//tx+start
	__bis_SR_register(CPUOFF + GIE);				// Enter LPM0 w/ interrupts
	FLAGS &= ~i2cTX;
	IE2 &= ~UCB0TXIE;
	UCB0CTL1 &=~UCTR;								//rx
	UCB0CTL1 |=	UCTXSTT;
	FLAGS &= ~RXed;
	IE2 |= UCB0RXIE;                        		//Enable RX interrupt
	__bis_SR_register(CPUOFF + GIE);            	// Enter LPM0 w/ interrupts
	UCB0CTL1 |= UCTXSTP;
	while (!(FLAGS & RXed));
	while (UCB0CTL1 & UCTXSTP);            			// Ensure stop condition got sent
	//P1OUT&=~LED0;
}

void i2cReadWord(unsigned char addr)
{
	while (UCB0CTL1 & UCTXSTP);
	UCB0CTL1 = UCSWRST;                     		//Enable SW reset
	UCB0CTL0 = UCMST + UCMODE_3 + UCSYNC;         	//I2C Master, synchronous mode
	UCB0CTL1 = UCSSEL_2 + UCSWRST;               	//Use SMCLK, keep SW reset
	UCB0BR0 = 12;                           		//fSCL = SMCLK/12 = ~100kHz
	UCB0BR1 = 0;
	UCB0I2CSA = Ti2cAddr;                     		//Slave Address
	UCB0CTL1 &= ~UCSWRST;                     		//Clear SW reset, resume operation
	IE2 |= UCB0TXIE;                        		//Enable TX interrupt
	IE2 &= ~UCB0RXIE;                        		//Enable RX interrupt
	FLAGS |=i2cTX;
	i2cBUF=addr;
	//P1OUT|=LED0;
	UCB0CTL1 |= UCTR + UCTXSTT;						//tx+start
	__bis_SR_register(CPUOFF + GIE);				// Enter LPM0 w/ interrupts
	FLAGS &= ~i2cTX;
	IE2 &= ~UCB0TXIE;
	UCB0CTL1 &=~UCTR;								//rx
	UCB0CTL1 |=	UCTXSTT;
	FLAGS &= ~RXed;
	IE2 |= UCB0RXIE;                        		//Enable RX interrupt
	__bis_SR_register(CPUOFF + GIE);            	//Enter LPM0 w/ interrupts
	i2cWORD=i2cBUF<<8;
	UCB0CTL1 |= UCTXSTP;							//send stop
	while (!(FLAGS & RXed));
	while (UCB0CTL1 & UCTXSTP);            			//Ensure stop condition got sent
	//i2cWORD|=i2cBUF;
	//P1OUT&=~LED0;

}
// ïèøåì áàéò â i2c ïî àäðåñó addr
void i2cSendByte(unsigned char addr, unsigned char byte)
{
	while (UCB0CTL1 & UCTXSTP);	// wait stop condition is sent
	UCB0CTL1 = UCSWRST;                     //Enable SW reset
	UCB0CTL0 = UCMST + UCMODE_3 + UCSYNC;         //I2C Master, synchronous mode
	UCB0CTL1 = UCSSEL_2 + UCSWRST;               //Use SMCLK, keep SW reset
	UCB0BR0 = 12;                           //fSCL = SMCLK/12 = ~100kHz
	UCB0BR1 = 0;
	UCB0I2CSA = Ti2cAddr;                     	//Slave Address
	UCB0CTL1 &= ~UCSWRST;                   //Clear SW reset, resume operation
	IE2 |= UCB0TXIE;                        //Enable TX interrupt
 	IE2 &= ~UCB0RXIE;                       //Enable RX interrupt
	FLAGS |=i2cTX;
	i2cBUF=addr;
	UCB0CTL1 |= UCTR + UCTXSTT; //tx+start
	__bis_SR_register(CPUOFF + GIE);            // Enter LPM0 w/ interrupts
	UCB0TXBUF=byte;
 	__bis_SR_register(CPUOFF + GIE);
	UCB0CTL1 |= UCTXSTP;               // I2C stop condition
	while (UCB0CTL1 & UCTXSTP);            // Ensure stop condition got sent
}

// ïèøåì áàéò â i2c ïî àäðåñó addr
void i2cSendCmd(unsigned char cmd)
{
	while (UCB0CTL1 & UCTXSTP);				// wait stop condition is sent
	UCB0CTL1 = UCSWRST;                    //Enable SW reset
	UCB0CTL0 = UCMST + UCMODE_3 + UCSYNC;   //I2C Master, synchronous mode
	UCB0CTL1 = UCSSEL_2 + UCSWRST;          //Use SMCLK, keep SW reset
	UCB0BR0 = 12;                           //fSCL = SMCLK/12 = ~100kHz
	UCB0BR1 = 0;
	UCB0I2CSA = Ti2cAddr;                   //Slave Address
	UCB0CTL1 &= ~UCSWRST;                   //Clear SW reset, resume operation
	IE2 |= UCB0TXIE;                        //Enable TX interrupt
 	IE2 &= ~UCB0RXIE;                       //Enable RX interrupt
	FLAGS |=i2cTX;
	i2cBUF=cmd;
	UCB0CTL1 |= UCTR + UCTXSTT; 			//tx+start
	__bis_SR_register(CPUOFF + GIE);        // Enter LPM0 w/ interrupts
	UCB0CTL1 |= UCTXSTP;               		// I2C stop condition
	while (UCB0CTL1 & UCTXSTP);            	// Ensure stop condition got sent
}

