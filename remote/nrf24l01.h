/*
 *  header
 *
 */


void NRF_init (void);
void CSN_LOW (void);
void CSN_HIGH (void);
void NRF_WRreg(unsigned char addr, unsigned char val);
void NRF_RDreg(unsigned char addr, unsigned char len);
unsigned char NRF_rdOneReg(unsigned char addr);
void NRF_cmd(unsigned char cmd, unsigned char len);
void NRF_transmit(unsigned char);
unsigned char NRF_status(void);
void NRF_readRX(unsigned char pw);
void NRF_irq_clear_all(void);
void NRF_flush_rx(void);
void NRF_flush_tx(void);
void NRF_2RX(void);
void NRF_2TX(void);
void NRF_up(void);
void NRF_down(void);
char waitNRF();
char NRF_broadcast_str(char* msg, char length);
char NRF_broadcast_char(unsigned char);

volatile unsigned char TXBuf[32];
volatile unsigned char RXBuf[32];
volatile unsigned char status, ack_pw;


// PINS

#define	CE		BIT3	//P1.3	NRF CE
#define	CSN		BIT4	//P1.4	NRF CSN

#define CSN_TIME      10

//SPI command defines
#define R_REGISTER		0x00
#define W_REGISTER		0x20
#define R_RX_PAYLOAD	0x61
#define W_TX_PAYLOAD	0xA0
#define FLUSH_TX		0xE1
#define FLUSH_RX		0xE2
#define REUSE_TX_PL		0xE3
#define NOP				0xFF

//SPI command data mask defines
#define R_REGISTER_DATA	0x1F
#define W_REGISTER_DATA	0x1F

////////////////////////////////////////////////////////////////////////////////////
// Register definitions
//
// Below are the defines for each register's address in the 24L01.
////////////////////////////////////////////////////////////////////////////////////
#define CONFIG			0x00
#define EN_AA			0x01
#define EN_RXADDR		0x02
#define SETUP_AW		0x03
#define SETUP_RETR		0x04
#define RF_CH			0x05
#define RF_SETUP		0x06
#define STATUS			0x07
#define OBSERVE_TX		0x08
#define RPD				0x09
#define RX_ADDR_P0		0x0A
#define RX_ADDR_P1		0x0B
#define RX_ADDR_P2		0x0C
#define RX_ADDR_P3		0x0D
#define RX_ADDR_P4		0x0E
#define RX_ADDR_P5		0x0F
#define TX_ADDR			0x10
#define RX_PW_P0		0x11
#define RX_PW_P1		0x12
#define RX_PW_P2		0x13
#define RX_PW_P3		0x14
#define RX_PW_P4		0x15
#define RX_PW_P5		0x16
#define FIFO_STATUS	0x17

////////////////////////////////////////////////////////////////////////////////////
// Default register values
//
// Below are the defines for each register's default value in the 24L01. Multi-byte
//   registers use notation B<X>, where "B" represents "byte" and <X> is the byte
//   number.
////////////////////////////////////////////////////////////////////////////////////
#define CONFIG_DEFAULT_VAL			0x08
#define EN_AA_DEFAULT_VAL			0x3F
#define EN_RXADDR_DEFAULT_VAL		0x03
#define SETUP_AW_DEFAULT_VAL		0x03
#define SETUP_RETR_DEFAULT_VAL		0x03
#define RF_CH_DEFAULT_VAL			0x02
#define RF_SETUP_DEFAULT_VAL		0x0E
#define STATUS_DEFAULT_VAL			0x0E
#define RX_ADDR_P0_B0_DEFAULT_VAL	0xE7
#define RX_ADDR_P0_B1_DEFAULT_VAL	0xE7
#define RX_ADDR_P0_B2_DEFAULT_VAL	0xE7
#define RX_ADDR_P0_B3_DEFAULT_VAL	0xE7
#define RX_ADDR_P0_B4_DEFAULT_VAL	0xE7
#define RX_ADDR_P1_B0_DEFAULT_VAL	0xC2
#define RX_ADDR_P1_B1_DEFAULT_VAL	0xC2
#define RX_ADDR_P1_B2_DEFAULT_VAL	0xC2
#define RX_ADDR_P1_B3_DEFAULT_VAL	0xC2
#define RX_ADDR_P1_B4_DEFAULT_VAL	0xC2
#define RX_ADDR_P2_DEFAULT_VAL		0xC3
#define RX_ADDR_P3_DEFAULT_VAL		0xC4
#define RX_ADDR_P4_DEFAULT_VAL		0xC5
#define RX_ADDR_P5_DEFAULT_VAL		0xC6
#define TX_ADDR_B0_DEFAULT_VAL		0xE7
#define TX_ADDR_B1_DEFAULT_VAL		0xE7
#define TX_ADDR_B2_DEFAULT_VAL		0xE7
#define TX_ADDR_B3_DEFAULT_VAL		0xE7
#define TX_ADDR_B4_DEFAULT_VAL		0xE7
#define RX_PW_P0_DEFAULT_VAL		0x00
#define RX_PW_P1_DEFAULT_VAL		0x00
#define RX_PW_P2_DEFAULT_VAL		0x00
#define RX_PW_P3_DEFAULT_VAL		0x00
#define RX_PW_P4_DEFAULT_VAL		0x00
#define RX_PW_P5_DEFAULT_VAL		0x00
#define FIFO_STATUS_DEFAULT_VAL		0x11

////////////////////////////////////////////////////////////////////////////////////
// Register bitwise definitions
//
// Below are the defines for each register's bitwise fields in the 24L01.
////////////////////////////////////////////////////////////////////////////////////
//CONFIG register bitwise definitions
#define CONFIG_RESERVED		0x80
#define	CONFIG_MASK_RX_DR	0x40
#define	CONFIG_MASK_TX_DS	0x20
#define	CONFIG_MASK_MAX_RT	0x10
#define	CONFIG_EN_CRC		0x08
#define	CONFIG_CRCO			0x04
#define	CONFIG_PWR_UP		0x02
#define	CONFIG_PRIM_RX		0x01

//EN_AA register bitwise definitions
#define EN_AA_RESERVED		0xC0
#define EN_AA_ENAA_ALL		0x3F
#define EN_AA_ENAA_P5		0x20
#define EN_AA_ENAA_P4		0x10
#define EN_AA_ENAA_P3		0x08
#define EN_AA_ENAA_P2		0x04
#define EN_AA_ENAA_P1		0x02
#define EN_AA_ENAA_P0		0x01
#define EN_AA_ENAA_NONE	0x00

//EN_RXADDR register bitwise definitions
#define EN_RXADDR_RESERVED	0xC0
#define EN_RXADDR_ERX_ALL	0x3F
#define EN_RXADDR_ERX_P5	0x20
#define EN_RXADDR_ERX_P4	0x10
#define EN_RXADDR_ERX_P3	0x08
#define EN_RXADDR_ERX_P2	0x04
#define EN_RXADDR_ERX_P1	0x02
#define EN_RXADDR_ERX_P0	0x01
#define EN_RXADDR_ERX_NONE	0x00

//SETUP_AW register bitwise definitions
#define SETUP_AW_RESERVED	0xFC
#define SETUP_AW			0x03
#define SETUP_AW_5BYTES		0x03
#define SETUP_AW_4BYTES		0x02
#define SETUP_AW_3BYTES		0x01
#define SETUP_AW_ILLEGAL	0x00

//SETUP_RETR register bitwise definitions
#define SETUP_RETR_ARD		0xF0
#define SETUP_RETR_ARD_4000	0xF0
#define SETUP_RETR_ARD_3750	0xE0
#define SETUP_RETR_ARD_3500	0xD0
#define SETUP_RETR_ARD_3250	0xC0
#define SETUP_RETR_ARD_3000	0xB0
#define SETUP_RETR_ARD_2750	0xA0
#define SETUP_RETR_ARD_2500	0x90
#define SETUP_RETR_ARD_2250	0x80
#define SETUP_RETR_ARD_2000	0x70
#define SETUP_RETR_ARD_1750	0x60
#define SETUP_RETR_ARD_1500	0x50
#define SETUP_RETR_ARD_1250	0x40
#define SETUP_RETR_ARD_1000	0x30
#define SETUP_RETR_ARD_750	0x20
#define SETUP_RETR_ARD_500	0x10
#define SETUP_RETR_ARD_250	0x00
#define SETUP_RETR_ARC		0x0F
#define SETUP_RETR_ARC_15	0x0F
#define SETUP_RETR_ARC_14	0x0E
#define SETUP_RETR_ARC_13	0x0D
#define SETUP_RETR_ARC_12	0x0C
#define SETUP_RETR_ARC_11	0x0B
#define SETUP_RETR_ARC_10	0x0A
#define SETUP_RETR_ARC_9	0x09
#define SETUP_RETR_ARC_8	0x08
#define SETUP_RETR_ARC_7	0x07
#define SETUP_RETR_ARC_6	0x06
#define SETUP_RETR_ARC_5	0x05
#define SETUP_RETR_ARC_4	0x04
#define SETUP_RETR_ARC_3	0x03
#define SETUP_RETR_ARC_2	0x02
#define SETUP_RETR_ARC_1	0x01
#define SETUP_RETR_ARC_0	0x00

//RF_CH register bitwise definitions
#define RF_CH_RESERVED		0x80

//RF_SETUP register bitwise definitions
#define RF_SETUP_RESERVED	0xE0
#define RF_SETUP_PLL_LOCK	0x10
#define RF_SETUP_RF_DR		0x08
#define RF_SETUP_RF_PWR		0x06
#define RF_SETUP_RF_PWR_0	0x06
#define RF_SETUP_RF_PWR_6 	0x04
#define RF_SETUP_RF_PWR_12	0x02
#define RF_SETUP_RF_PWR_18	0x00
#define RF_SETUP_LNA_HCURR	0x01

//STATUS register bitwise definitions
#define STATUS_RESERVED						0x80
#define STATUS_RX_DR						0x40
#define STATUS_TX_DS						0x20
#define STATUS_MAX_RT						0x10
#define STATUS_RX_P_NO						0x0E
#define STATUS_RX_P_NO_RX_FIFO_NOT_EMPTY	0x0E
#define STATUS_RX_P_NO_UNUSED				0x0C
#define STATUS_RX_P_NO_5					0x0A
#define STATUS_RX_P_NO_4					0x08
#define STATUS_RX_P_NO_3					0x06
#define STATUS_RX_P_NO_2					0x04
#define STATUS_RX_P_NO_1					0x02
#define STATUS_RX_P_NO_0					0x00
#define STATUS_TX_FULL						0x01

//OBSERVE_TX register bitwise definitions
#define OBSERVE_TX_PLOS_CNT	0xF0
#define OBSERVE_TX_ARC_CNT		0x0F

//CD register bitwise definitions
#define CD_RESERVED	0xFE
#define CD_CD			0x01

//RX_PW_P0 register bitwise definitions
#define RX_PW_P0_RESERVED	0xC0

//RX_PW_P0 register bitwise definitions
#define RX_PW_P0_RESERVED	0xC0

//RX_PW_P1 register bitwise definitions
#define RX_PW_P1_RESERVED	0xC0

//RX_PW_P2 register bitwise definitions
#define RX_PW_P2_RESERVED	0xC0

//RX_PW_P3 register bitwise definitions
#define RX_PW_P3_RESERVED	0xC0

//RX_PW_P4 register bitwise definitions
#define RX_PW_P4_RESERVED	0xC0

//RX_PW_P5 register bitwise definitions
#define RX_PW_P5_RESERVED	0xC0

//FIFO_STATUS register bitwise definitions
#define FIFO_STATUS_RESERVED	0x8C
#define FIFO_STATUS_TX_REUSE	0x40
#define FIFO_STATUS_TX_FULL	0x20
#define FIFO_STATUS_TX_EMPTY	0x10
#define FIFO_STATUS_RX_FULL	0x02
#define FIFO_STATUS_RX_EMPTY	0x01

