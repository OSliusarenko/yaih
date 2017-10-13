#include "PCD8544.h"

void writeStringToLCD(const char *string, _Bool fnt) {
while(*string) {
writeCharToLCD(*string++, fnt);
}
}

void writeCharToLCD(char c, _Bool fnt) {
    unsigned char i;
    for(i = 0; i < 5; i++) {
        if (fnt) writeToLCD(LCD5110_DATA, ~(font[c - 0x20][i]));
          else writeToLCD(LCD5110_DATA, font[c - 0x20][i]);
    }
    if (fnt) writeToLCD(LCD5110_DATA, 0xFF);
      else writeToLCD(LCD5110_DATA, 0);
}

void writeIntToLCD(char i)
{
    if (i < 0)
    {
        writeCharToLCD('-', FNT_NORMAL);
        i *= -1;
    };

    writeCharToLCD(i/10+0x30, FNT_NORMAL);
    writeCharToLCD(i%10+0x30, FNT_NORMAL);

};

void writeGraphicToLCD(char *byte, char size) {
    while(size--) writeToLCD(LCD5110_DATA, *byte++);
}

void writeToLCD(unsigned char dataCommand, unsigned char data) {
LCD5110_SELECT;
if(dataCommand) {
LCD5110_SET_DATA;
} else {
LCD5110_SET_COMMAND;
}
UCB0TXBUF = data;
while(!(IFG2 & UCB0TXIFG))
;
LCD5110_DESELECT;
}

void clearLCD() {
setAddr(0, 0);
int c = 0;
while(c < PCD8544_MAXBYTES) {
writeToLCD(LCD5110_DATA, 0);
c++;
}
setAddr(0, 0);
}

void clearBank(unsigned char bank) {
setAddr(0, bank);
int c = 0;
while(c < PCD8544_HPIXELS) {
writeToLCD(LCD5110_DATA, 0);
c++;
}
setAddr(0, bank);
}

void setAddr(unsigned char xAddr, unsigned char yAddr) {
writeToLCD(LCD5110_COMMAND, PCD8544_SETXADDR | xAddr);
writeToLCD(LCD5110_COMMAND, PCD8544_SETYADDR | yAddr);
}

void initLCD() {
writeToLCD(LCD5110_COMMAND, PCD8544_FUNCTIONSET | PCD8544_EXTENDEDINSTRUCTION);
writeToLCD(LCD5110_COMMAND, PCD8544_SETVOP | 0x3F);
writeToLCD(LCD5110_COMMAND, PCD8544_SETTEMP | 0x02);
writeToLCD(LCD5110_COMMAND, PCD8544_SETBIAS | 0x03);
writeToLCD(LCD5110_COMMAND, PCD8544_FUNCTIONSET);
writeToLCD(LCD5110_COMMAND, PCD8544_DISPLAYCONTROL | PCD8544_DISPLAYNORMAL);
}

void LCDoff() {
writeToLCD(LCD5110_COMMAND, PCD8544_FUNCTIONSET | PCD8544_POWERDOWN);
}

void LCDon() {
writeToLCD(LCD5110_COMMAND, PCD8544_FUNCTIONSET);
}
