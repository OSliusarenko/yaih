#include "nrf24l01.h"
#include "spi.c"

void CSN_HIGH (void)
{
P1OUT |= CSN;
}

void CSN_LOW (void)
{
delay (CSN_TIME);
P1OUT &= ~CSN;
}

void CE_HIGH(void)
{
P1OUT |= CE;
}

void CE_LOW(void)
{
	P1OUT &= ~CE;
}

void NRF_init(void)
{
	
	/* CE */
	P1OUT &= ~CE;	//CE LOW
	P1DIR |= CE;
	/* CSN */
    P1OUT  |= CSN;	//CSN HIGH
    P1DIR  |= CSN;

	SPI_init();

	//en_aa
    TXBuf[0]=0x3f;
    NRF_WRreg(0x01, 1);
    //en_rx_addr
    TXBuf[0]=0x03;
    NRF_WRreg(0x02, 1);
    //setup_aw
    TXBuf[0]=0x03;
    NRF_WRreg(0x03, 1);
    //setup_retr
    TXBuf[0]=0x3f;
    NRF_WRreg(0x04, 1);
    //rf_ch
    TXBuf[0]=85;
    NRF_WRreg(0x05, 1);
    //rf_setup
    TXBuf[0]=0b111; // 1Mbps max pwr hi-gain LNA
    NRF_WRreg(0x06, 1);
    //rx_addr_p0
    TXBuf[0] = 0xe7;
    TXBuf[1] = 0xe7;
    TXBuf[2] = 0xe7;
    TXBuf[3] = 0xe7;
    TXBuf[4] = 0xe7;
    NRF_WRreg(0x0a, 5);
    //rx_addr_p1
    TXBuf[0] = 0xc2;
    TXBuf[1] = 0xc2;
    TXBuf[2] = 0xc2;
    TXBuf[3] = 0xc2;
    TXBuf[4] = 0xc2;
    NRF_WRreg(0x0b, 5);
    //rx_addr_p2
    TXBuf[0] = 0xc3;
    NRF_WRreg(0x0c, 1);
    //rx_addr_p3
    TXBuf[0] = 0xc4;
    NRF_WRreg(0x0d, 1);
    //rx_addr_p4
    TXBuf[0] = 0xc5;
    NRF_WRreg(0x0e, 1);
    //rx_addr_p5
    TXBuf[0] = 0xc6;
    NRF_WRreg(0x0f, 1);
    //tx_addr
    TXBuf[0] = 0xe7;
    TXBuf[1] = 0xe7;
    TXBuf[2] = 0xe7;
    TXBuf[3] = 0xe7;
    TXBuf[4] = 0xe7;
    NRF_WRreg(0x10, 5);

    //rx_payload_width_p0
    TXBuf[0] = 8;
    NRF_WRreg(0x11, 1);

    //rx_payload_width_p1
    TXBuf[0] = 8;
    NRF_WRreg(0x12, 1);

    //rx_payload_width_p2
    TXBuf[0] = 0;
    NRF_WRreg(0x13, 1);

    //rx_payload_width_p3
    TXBuf[0] = 0;
    NRF_WRreg(0x14, 1);

    //rx_payload_width_p4
    TXBuf[0] = 0;
    NRF_WRreg(0x15, 1);

    //rx_payload_width_p5
    TXBuf[0] = 0;
    NRF_WRreg(0x16, 1);
    
    //FEATURE
    TXBuf[0] = 0x06;
    NRF_WRreg(0x1d, 1);

    //DYNPD
    TXBuf[0] = 0x3f;
    NRF_WRreg(0x1c, 1);


    //power up
    TXBuf[0]= 0xe;
    if(defaultRX){TXBuf[0]|= CONFIG_PRIM_RX;}	// default rx or tx
    NRF_WRreg(0x00, 1);
    if (defaultRX)
    {
    	CE_HIGH();
    }
    else
    {
    	CE_LOW();
    }
    
    delay_10us(3);

}

void NRF_WRreg(unsigned char addr, unsigned char len)
{
	unsigned char ind=0;
	unsigned char res;
	CSN_LOW();
	res=SPI_txByte(W_REGISTER|(W_REGISTER_DATA&addr));
//	putChar(0x0a);
//	putChar(0x0d);
//	putChar('W');
//	putChar(':');
//	hex2uart(addr>>4);
//	hex2uart(addr);
//	putChar('-');
	while(ind<len)
	{
		res=SPI_txByte(TXBuf[ind]);
//		hex2uart(TXBuf[ind]>>4);
//		hex2uart(TXBuf[ind]);
		ind++;
	}
	CSN_HIGH();
}


void NRF_RDreg(unsigned char addr, unsigned char len)
{
	unsigned char ind=0;
	CSN_LOW();
	status=SPI_txByte(R_REGISTER|(R_REGISTER_DATA&addr));
	while(ind<len)
	{
		RXBuf[ind]=SPI_txByte(NOP);
		ind++;
	}
	CSN_HIGH();
}

unsigned char NRF_rdOneReg(unsigned char addr)
{
	unsigned char oneReg;
	CSN_LOW();
	status=SPI_txByte(R_REGISTER|(R_REGISTER_DATA&addr));
	oneReg=SPI_txByte(NOP);
	CSN_HIGH();
	return oneReg;
}


void NRF_cmd(unsigned char cmd, unsigned char len)
{
	unsigned char ind=0;
	unsigned char res;
	CSN_LOW();
	res=SPI_txByte(cmd);
	while(ind<len)
	{
		RXBuf[ind]=SPI_txByte(TXBuf[ind]);
		ind++;
	}
	CSN_HIGH();
    __delay_cycles(1000); // check out this value !!!
}

void NRF_transmit(unsigned char payloadWidth)
{
    unsigned char stat;
    NRF_cmd(W_TX_PAYLOAD, payloadWidth);  
	CE_HIGH();
	delay_10us(3);
	CE_LOW();
}

void NRF_readRX(unsigned char pw)
{
	CE_LOW();
	NRF_cmd(R_RX_PAYLOAD,pw);
	CE_HIGH();
}

void NRF_irq_clear_all(void)
{
	TXBuf[0]=STATUS_RX_DR | STATUS_TX_DS | STATUS_MAX_RT;
	NRF_WRreg(STATUS,1);
}

unsigned char NRF_status(void)
{
	CSN_LOW();
	status=SPI_txByte(R_REGISTER|CONFIG);
	CSN_HIGH();
	return status;
}


void NRF_flush_rx(void)
{
	CSN_LOW();
	status=SPI_txByte(FLUSH_RX);
	CSN_HIGH();

}

void NRF_flush_tx(void)
{
	CSN_LOW();
	status=SPI_txByte(FLUSH_TX);
	CSN_HIGH();

}
void NRF_2RX(void)
{
	TXBuf[0]=NRF_rdOneReg(CONFIG);
	TXBuf[0] |= CONFIG_PRIM_RX;
	NRF_WRreg(CONFIG,1);
	CE_HIGH();
}

void NRF_2TX (void)
{
	TXBuf[0]=NRF_rdOneReg(CONFIG);
	TXBuf[0] &= ~CONFIG_PRIM_RX;
	NRF_WRreg(CONFIG,1);
	CE_LOW();
}

void NRF_up(void)
{
	TXBuf[0]=NRF_rdOneReg(CONFIG);
	TXBuf[0] |= CONFIG_PWR_UP;
	NRF_WRreg(CONFIG,1);
	CE_LOW();
}

void NRF_down(void)
{
	NRF_irq_clear_all();
	TXBuf[0]=NRF_rdOneReg(CONFIG);
	TXBuf[0] &= ~CONFIG_PWR_UP;
	NRF_WRreg(CONFIG,1);
	CE_LOW();
}

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
        return 1;
    }    
    if(tmp & STATUS_TX_DS)
    {
        NRF_flush_tx();
        return 2;
    }
    if(tmp & STATUS_MAX_RT)
    {
        NRF_flush_tx();
        NRF_flush_rx();
        return 3;
    }
    return 0;
};

char NRF_broadcast_str(char* msg, char length)
{
    unsigned char c, l=32;
    
    if (l>length) l = length;
    
    for (c=0; c<l; c++) TXBuf[c] = msg[c];

    NRF_transmit(l);
    
    return 0;
};

char NRF_broadcast_char(unsigned char cc)
{
    TXBuf[0] = cc;

    NRF_transmit(1);

    return 0;
}
