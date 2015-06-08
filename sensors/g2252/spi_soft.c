#define MSCK BIT7
#define MMISO BIT3
#define MMOSI BIT4

void SPI_init(void);
unsigned char SPI_txByte(unsigned char byte);


void SPI_init(void)
{
    P1DIR |= MSCK + MMOSI;
    P1DIR &= ~MMISO;
};

unsigned char SPI_txByte(unsigned char byte)
{
    unsigned char i;
    for( i = 0; i < 8; i++ ) 
    {
        // Put bits on the line, most significant bit first.
        if( byte & 0x80 ) {
           P1OUT |= MMOSI;
        } else {
           P1OUT &= ~MMOSI;
        }
        byte <<= 1;

        __delay_cycles( 1 );
        P1OUT |= MSCK;

        __delay_cycles( 1 );        
        if(P1IN & MMISO)
        {
            byte |= 0x01; // LSBF
        } else
        {
            byte &= ~0x01;
        };
        
        P1OUT &= ~MSCK;

    }
    
       
    return byte;
}
