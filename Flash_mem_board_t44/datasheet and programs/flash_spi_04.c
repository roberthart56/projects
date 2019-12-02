//
// hello.nRF24L01P.44.c
//
// nRF24L01+ 9600 baud FTDI SPI bridge (under development)
//    no fuse
//
// Neil Gershenfeld
//    11/29/16
//
// (c) Massachusetts Institute of Technology 2016
// This work may be reproduced, modified, distributed,
// performed, and displayed for any purpose. Copyright is
// retained and must be preserved. The work is provided
// as is; no warranty is provided, and users accept all 
// liability.
//
// includes
//
#include <avr/io.h>
#include <util/delay.h>
//
// macros
//
#define output(directions,pin) (directions |= pin) // set port direction for output
#define set(port,pin) (port |= pin) // set port pin
#define clear(port,pin) (port &= (~pin)) // clear port pin
#define pin_test(pins,pin) (pins & pin) // test for port pin
#define bit_test(byte,bit) (byte & (1 << bit)) // test for bit set
#define bit_delay_time 102 // bit delay in us for 9600 with overhead at 8 MHz
#define bit_delay() _delay_us(bit_delay_time) // RS232 bit delay
#define half_bit_delay() _delay_us(bit_delay_time/2) // RS232 half bit delay
#define char_delay() _delay_ms(10) // char delay
#define SPI_delay() _delay_us(1) // SPI delay
//
// define serial
//
#define serial_port PORTA
#define serial_direction DDRA
#define serial_pins PINA
#define serial_pin_in (1 << PA0)
#define serial_pin_out (1 << PA1)
//
// define pins
//
#define CS_port PORTB
#define CS_direction DDRB
#define CS_pin (1 << PB2)
#define SCK_port PORTB
#define SCK_direction DDRB
#define SCK_pin (1 << PB0)
#define MOSI_port PORTB
#define MOSI_direction DDRB
#define MOSI_pin (1 << PB1)
#define MISO_pins PINA
#define MISO_direction DDRA
#define MISO_pin (1 << PA7)

#define button_port PORTA		// The button is on port A
#define button_direction DDRA	//  DDRA defines input/output for port A
#define button_pin (1 << PA4)	//  The button is on pin 4 of port A
#define button_pins PINA			//  PINA is the register that is read to detect input high or low.
#define LED_port PORTA		//  port A will be used for the LED
#define LED_direction DDRA	//  Direction port for LED
#define LED_pin (1 << PA3)	// LED ON PA3 (PHYSICAL PIN 10)

//
// define commands
//
#define READ_ST_REG_1 0X05
#define READ_ST_REG_2 0X35
#define READ_ST_REG_3 0X15
#define WRITE_ENABLE 0X06
#define READ_DATA 0X03
#define WRITE_DATA 0X02
#define SECTOR_ERASE 0X20
#define BLOCK_ERASE32 0X52
#define BLOCK_ERASE64 0XD8
#define CHIP_ERASE 0XC7

// define registers
//
#define CONFIG 0x00

//
// get_char
//    read character into rxbyte on pins pin
//    assumes line driver (inverts bits)
//
//
void get_char(volatile unsigned char *pins, unsigned char pin, char *rxbyte) {
   *rxbyte = 0;
   while (pin_test(*pins,pin))
      //
      // wait for start bit
      //
      ;
   //
   // delay to middle of first data bit
   //
   half_bit_delay();
   bit_delay();
   //
   // unrolled loop to read data bits
   //
   if pin_test(*pins,pin)
      *rxbyte |= (1 << 0);
   else
      *rxbyte |= (0 << 0);
   bit_delay();
   if pin_test(*pins,pin)
      *rxbyte |= (1 << 1);
   else
      *rxbyte |= (0 << 1);
   bit_delay();
   if pin_test(*pins,pin)
      *rxbyte |= (1 << 2);
   else
      *rxbyte |= (0 << 2);
   bit_delay();
   if pin_test(*pins,pin)
      *rxbyte |= (1 << 3);
   else
      *rxbyte |= (0 << 3);
   bit_delay();
   if pin_test(*pins,pin)
      *rxbyte |= (1 << 4);
   else
      *rxbyte |= (0 << 4);
   bit_delay();
   if pin_test(*pins,pin)
      *rxbyte |= (1 << 5);
   else
      *rxbyte |= (0 << 5);
   bit_delay();
   if pin_test(*pins,pin)
      *rxbyte |= (1 << 6);
   else
      *rxbyte |= (0 << 6);
   bit_delay();
   if pin_test(*pins,pin)
      *rxbyte |= (1 << 7);
   else
      *rxbyte |= (0 << 7);
   //
   // wait for stop bit
   //
   bit_delay();
   half_bit_delay();
   }
//
// put_char
//    send character in txchar on port pin
//    assumes line driver (inverts bits)
//
void put_char(volatile unsigned char *port, unsigned char pin, char txchar) {
   //
   // start bit
   //
   clear(*port,pin);
   bit_delay();
   //
   // unrolled loop to write data bits
   //
   if bit_test(txchar,0)
      set(*port,pin);
   else
      clear(*port,pin);
   bit_delay();
   if bit_test(txchar,1)
      set(*port,pin);
   else
      clear(*port,pin);
   bit_delay();
   if bit_test(txchar,2)
      set(*port,pin);
   else
      clear(*port,pin);
   bit_delay();
   if bit_test(txchar,3)
      set(*port,pin);
   else
      clear(*port,pin);
   bit_delay();
   if bit_test(txchar,4)
      set(*port,pin);
   else
      clear(*port,pin);
   bit_delay();
   if bit_test(txchar,5)
      set(*port,pin);
   else
      clear(*port,pin);
   bit_delay();
   if bit_test(txchar,6)
      set(*port,pin);
   else
      clear(*port,pin);
   bit_delay();
   if bit_test(txchar,7)
      set(*port,pin);
   else
      clear(*port,pin);
   bit_delay();
   //
   // stop bit
   //
   set(*port,pin);
   bit_delay();
   //
   // char delay
   //
   bit_delay();
   }
//
// SPI_read_status - protocal for nrf24l01, not flash chip.
//    read status register
//
// void SPI_read_status(unsigned char *ret) {
//    unsigned char bit;
//    //
//    // init
//    //
//    *ret = 0;
//    clear(SCK_port,SCK_pin);
//    clear(CS_port,CS_pin);
//    SPI_delay();
//    //
//    // bit loop
//    //
//    for (bit = 0; bit < 8; ++bit) {
//       clear(MOSI_port,MOSI_pin);
//       SPI_delay();
//       set(SCK_port,SCK_pin);
//       SPI_delay();
//       if pin_test(MISO_pins,MISO_pin)
//          *ret |= (1 << (7-bit));
//       clear(SCK_port,SCK_pin);
//       SPI_delay();
//       }
//    //
//    // finish
//    //
//    set(CS_port,CS_pin);
//    }
   //
   // SPI_write enable
   //    read status register
   //
   void SPI_read_status(unsigned char *ret) {
      unsigned char bit;
      unsigned char cmd = READ_ST_REG_1;
	  //
      // init
      //
      *ret = 0;
      clear(MOSI_port,MOSI_pin);
	  clear(SCK_port,SCK_pin);
      clear(CS_port,CS_pin);
      SPI_delay();
      //
      // bit loop to send byte
      //
	  for (bit = 0; bit < 8; ++bit) {
		  //if bit_test(cmd, (7 - bit)) set(MOSI_port, MOSI_pin);
		 //else clear(MOSI_port, MOSI_pin);
		 if (cmd & (1 << (7 - bit))) set(MOSI_port, MOSI_pin);
		 else clear(MOSI_port, MOSI_pin);
		 SPI_delay();
		 set(SCK_port,SCK_pin);
         SPI_delay();
         clear(SCK_port,SCK_pin);
         }
		 
      clear(MOSI_port,MOSI_pin);  //this should not matter.
	  //
      // bit loop to read byte
      //
	  for (bit = 0; bit < 8; ++bit) {
         clear(SCK_port,SCK_pin);      //redundant on first time around - pin already clear.
         SPI_delay();
         if pin_test(MISO_pins,MISO_pin)   //first time around reads MSB
            *ret |= (1 << (7-bit));
         set(SCK_port,SCK_pin);
         SPI_delay();
		 
         }
      //
      // finish
      //
      set(CS_port,CS_pin);
      }
	  
	  //
	  // Read memory address
	  //
	  
      void SPI_read(unsigned char *ret, unsigned char addr1, unsigned char addr2,  unsigned char addr3) {
         unsigned char bit,ind;
         unsigned char cmd = READ_DATA;
		 unsigned char add[4]={cmd,addr1,addr2,addr3};
   	  //
         // init
         //
         *ret = 0;
         clear(MOSI_port,MOSI_pin);
   	  clear(SCK_port,SCK_pin);
         clear(CS_port,CS_pin);
         SPI_delay();
         //
         // bit loop to send byte
         //
	  for (ind = 0; ind < 4; ++ind) {
	   	  for (bit = 0; bit < 8; ++bit) {
	   		  //if bit_test(cmd, (7 - bit)) set(MOSI_port, MOSI_pin);
	   		 //else clear(MOSI_port, MOSI_pin);
	   		 if (add[ind] & (1 << (7 - bit))) set(MOSI_port, MOSI_pin);
	   		 else clear(MOSI_port, MOSI_pin);
	   		 SPI_delay();
	   		 set(SCK_port,SCK_pin);
	            SPI_delay();
	            clear(SCK_port,SCK_pin);
	       }
		}
         clear(MOSI_port,MOSI_pin);  //this should not matter.
   	  //
         // bit loop to read byte
         //
   	  for (bit = 0; bit < 8; ++bit) {
            clear(SCK_port,SCK_pin);      //redundant on first time around - pin already clear.
            SPI_delay();
            if pin_test(MISO_pins,MISO_pin)   //first time around reads MSB
               *ret |= (1 << (7-bit));
            set(SCK_port,SCK_pin);
            SPI_delay();
		 
            }
         //
         // finish
         //
         set(CS_port,CS_pin);
         }
	  //
	  // SPI Write Enable Command
	  //
      void SPI_write_enable() {
         unsigned char bit;
         unsigned char cmd = WRITE_ENABLE;
   	  //
         // init
         //
         clear(MOSI_port,MOSI_pin);
   	     clear(SCK_port,SCK_pin);
         clear(CS_port,CS_pin);
         SPI_delay();
         //
         // bit loop to send byte
         //
   	  for (bit = 0; bit < 8; ++bit) {
            if bit_test(cmd, (7 - bit)) set(MOSI_port, MOSI_pin);
   		 else clear(MOSI_port, MOSI_pin);
   		 SPI_delay();
   		 set(SCK_port,SCK_pin);
            SPI_delay();
            clear(SCK_port,SCK_pin);
            }
		 
			SPI_delay();
         set(CS_port,CS_pin);
         }
//
// SPI_write_command
//    write SPI command
//
		 
   	  //
   	  // Read memory address
   	  //
	  
    void SPI_command(unsigned char cmd, unsigned char addr1, unsigned char addr2,  unsigned char addr3, unsigned char nbytes, unsigned char databyte) {		//make array of command, address, data
		unsigned char bit,ind;
		unsigned char addr[3] = {addr1, addr2, addr3};
		unsigned char send[4 + nbytes];
		send[0] = cmd;
		for (ind= 1; ind < 4; ++ind) {
			send[ind] = addr[ind-1];
		}
		send[4] = databyte;
		
		
		
		
		
		  	  //
		        // init
		        //
		clear(MOSI_port,MOSI_pin);
		clear(SCK_port,SCK_pin);
		clear(CS_port,CS_pin);
		SPI_delay();
		        //
            // bit loop to send bytes of command and data
            //
			for (ind = 0; ind < 5; ++ind) {
				for (bit = 0; bit < 8; ++bit) {
					if (send[ind] & (1 << (7 - bit))) set(MOSI_port, MOSI_pin);
					else clear(MOSI_port, MOSI_pin);
					SPI_delay();
					set(SCK_port,SCK_pin);
					SPI_delay();
					clear(SCK_port,SCK_pin);
				}
			}
		clear(MOSI_port,MOSI_pin);  //this should not matter.
		    //
		    // finish
		    //
		set(CS_port,CS_pin);
	}
			
			
			
//void SPI_write(unsigned char command,unsigned char bytes,unsigned char *write_buffer,unsigned char *read_buffer) {
   //
   // to be written
   //
  // }
//
// SPI_read_command
//    read SPI command
//
//void SPI_read(unsigned char command,unsigned char bytes,unsigned char *write_buffer,unsigned char *read_buffer) {
   //
   // to be written
   //
  // }
//
// main
//
int main(void) {
   static unsigned char ret;
   //
   // set clock divider to /1
   //
   CLKPR = (1 << CLKPCE);
   CLKPR = (0 << CLKPS3) | (0 << CLKPS2) | (0 << CLKPS1) | (0 << CLKPS0);
   //
   // initialize output pins
   //
   set(serial_port,serial_pin_out);
   output(serial_direction,serial_pin_out);
   set(CS_port,CS_pin);
   output(CS_direction,CS_pin);
   output(SCK_direction,SCK_pin);
   clear(MOSI_port,MOSI_pin);
   output(MOSI_direction,MOSI_pin);
   clear(MISO_direction,MISO_pin);   //set MISO pin for input
   
   SPI_write_enable();  //write enable oncer
   SPI_command(WRITE_DATA,0,0,5, 1, 0XAE);	
   // main loop
   //
   while (1) {
	  
	  SPI_read(&ret,0,0,5);   //read from memory location 0.
      put_char(&serial_port,serial_pin_out,ret);
	  //put_char(&serial_port,serial_pin_out,0xAA);
      char_delay();
      //
      // to be written
      //
      }
   }
