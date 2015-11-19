//P1.5	NRF SCK
//P1.6	NRF MISO
//P1.7	NRF MOSI

void SPI_init(void);
unsigned char SPI_txByte(unsigned char byte);


void SPI_init(void)
{
    // 3-pin, 8-bit SPI master
    USICTL0 = USISWRST; 
    USICTL0 |= USIPE7 + USIPE6 + USIPE5 + USIMST + USIOE; // Port, SPI Master
    USICTL1 |= USICKPH;               // Counter interrupt,
    USICKCTL = USISSEL_2;          // /2 SMCLK
    USICTL0 &= ~USISWRST;                     // USI released for operation
};

 unsigned char SPI_txByte(unsigned char byte)
{
	USISRL = byte;
    USICNT = 8;    // init-load counter
    
    while (!(USIIFG & USICTL1));            // Counter clear?
	    
    unsigned char tmp = USISRL;
        
    return tmp;
}
