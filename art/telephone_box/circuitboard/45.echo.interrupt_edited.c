//
//
// 45.echo.interrupt.c
//
// 115200 baud FTDI character echo, interrupt version
//
//
//
// Neil Gershenfeld
// 12/8/10
//
// (c) Massachusetts Institute of Technology 2010
// This work may be reproduced, modified, distributed,
// performed, and displayed for any purpose. Copyright is
// retained and must be preserved. The work is provided
// as is; no warranty is provided, and users accept all
// liability.
//

#include <avr/io.h>
#include <util/delay.h>
#include <avr/interrupt.h>
#include <avr/pgmspace.h>

#define output(directions,pin) (directions |= pin) // set port direction for output
#define set(port,pin) (port |= pin) // set port pin
#define clear(port,pin) (port &= (~pin)) // clear port pin
#define pin_test(pins,pin) (pins & pin) // test for port pin
#define bit_test(byte,bit) (byte & (1 << bit)) // test for bit set
#define bit_delay_time 102 // bit delay for 115200 with overhead
#define bit_delay() _delay_us(bit_delay_time) // RS232 bit delay
#define half_bit_delay() _delay_us(bit_delay_time/2) // RS232 half bit delay
#define char_delay() _delay_ms(10) // char delay

#define serial_port PORTB
#define serial_direction DDRB
#define serial_pins PINB
#define serial_pin_in (1 << PB0)
#define serial_pin_out (1 << PB2)
#define serial_interrupt (1 << PCIE)
#define serial_interrupt_pin (1 << PCINT0)

#define motor_port PORTB
#define motor_direction DDRB
#define motor_pin (1 << PB1)


#define max_buffer 25

volatile uint8_t PWM_level;

void get_char(volatile unsigned char *pins, unsigned char pin, char *rxbyte) {
   //
   // read character into rxbyte on pins pin
   //    assumes line driver (inverts bits)
   //
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

void put_char(volatile unsigned char *port, unsigned char pin, char txchar) {
   //
   // send character in txchar on port pin
   //    assumes line driver (inverts bits)
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
   }



ISR(PCINT0_vect) {
   //
   // pin change interrupt handler
   //
   clear (PCMSK, serial_interrupt_pin);  //disable pin change during ISR

   //clear(motor_port, motor_pin);
   static char chr;

   get_char(&serial_pins, serial_pin_in, &chr);
   PWM_level = chr;
   put_char(&serial_port, serial_pin_out, chr);


   set (PCMSK, serial_interrupt_pin);    //re-enable pin change on interrupt pin.
   }

int main(void) {
   //
   // main
   //
   // set clock divider to /1
   //
   CLKPR = (1 << CLKPCE);
   CLKPR = (0 << CLKPS3) | (0 << CLKPS2) | (0 << CLKPS1) | (0 << CLKPS0);

/*
   Control Register A for Timer/Counter-0 (Timer/Counter-0 is configured using two registers: A and B)
   TCCR0A is 8 bits: [COM0A1:COM0A0:COM0B1:COM0B0:unused:unused:WGM01:WGM00]
   2<<COM0A0: sets bits COM0A0(0) and COM0A1(1), which (in Fast PWM mode) clears OC0A on compare-match, and sets OC0A at BOTTOM
   2<<COM0B0: sets bits COM0B0(0) and COM0B1(1), which (in Fast PWM mode) clears OC0B on compare-match, and sets OC0B at BOTTOM
   3<<WGM00: sets bits WGM00 and WGM01, which (when combined with WGM02 from TCCR0B below) enables Fast PWM mode
   */
   TCCR0A = 2<<COM0B0 | 3<<WGM00;

   /*
   Control Register B for Timer/Counter-0 (Timer/Counter-0 is configured using two registers: A and B)
   TCCR0B is 8 bits: [FOC0A:FOC0B:unused:unused:WGM02:CS02:CS01:CS00]
   0<<WGM02: bit WGM02 remains clear, which (when combined with WGM00 and WGM01 from TCCR0A above) enables Fast PWM mode
   CS00-CS02 set prescalar, in this case /256 which makes PWM period = 256*256/8 microseconds, or 8.2 milliseconds.
   */
   //TCCR0B = 0<<WGM02 | 1<<CS02| 0<<CS01| 0<<CS00;  // divide by 256
   TCCR0B = 0<<WGM02 | 0<<CS02| 1<<CS01| 1<<CS00;  // divide by 64  (011) for ~2ms period.

   //
   // initialize output pins
   //
   set(serial_port, serial_pin_out);
   output(serial_direction, serial_pin_out);
   output(motor_direction, motor_pin);

   //
   // set up pin change interrupt on input pin
   //
   set(GIMSK, serial_interrupt);
   set (PCMSK, serial_interrupt_pin);
   sei();
   //
   // main loop
   //
   while (1) {
      //set(motor_port, motor_pin);
      OCR0B =PWM_level;			// update 0CR0A to set PWM duty cycle
      //
      // wait for interrupt
      //
      ;
      }
   }
