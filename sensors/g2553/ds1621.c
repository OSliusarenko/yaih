#define	Ti2cAddr						0x48
#define DS1621_CMD_ACCESSCONFIG        	0xAC
#define DS1621_CMD_INITIATECONVERT     	0xEE
#define DS1621_CMD_ACCESSTEMPERATURE   	0xAA
#define DS1621_CMD_READ_COUNTER_REMAIN 	0xA8
#define CONVERSION_DONE 				BIT7

void termInit(void);
void termDown(void);


void termInit(void)
{
	//init i2c
    P1OUT  |= CSN;	//CSN HIGH
    P1DIR  |= CSN;

    i2cPortSEL |= i2cSDA + i2cSCK;                     	//Set I2C pins
	i2cPortSEL2 |= i2cSDA + i2cSCK;
	TPWRPortOUT |= TPWR;
	TPWRPortDIR |= TPWR;
	//P1OUT |= LED0;
	i2cSendByte(DS1621_CMD_ACCESSCONFIG,0x01);			//one shot conversion
	i2cSendCmd(DS1621_CMD_INITIATECONVERT);
}

void termDown(void)
{
	TPWRPortOUT &= ~TPWR;
	TPWRPortDIR |= TPWR;
	i2cPortSEL &= ~(i2cSDA + i2cSCK);                     	//reset I2C pins
	i2cPortSEL2 &= ~(i2cSDA + i2cSCK);
	P1OUT &= ~LED0;
}
