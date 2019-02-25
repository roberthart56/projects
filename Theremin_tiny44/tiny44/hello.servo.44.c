//
// hello.servo.44.c
//
// servo motor hello-world
//
// set lfuse to 0x5E for 20 MHz xtal
//
// Neil Gershenfeld
// 4/8/12
//
// (c) Massachusetts Institute of Technology 2012
// This work may be reproduced, modified, distributed,
// performed, and displayed for any purpose. Copyright is
// retained and must be preserved. The work is provided
// as is; no warranty is provided, and users accept all 
// liability.
//

#include <avr/io.h>
#include <util/delay.h>

#define output(directions,pin) (directions |= pin) // set port direction for output
#define set(port,pin) (port |= pin) // set port pin
#define clear(port,pin) (port &= (~pin)) // clear port pin
#define pin_test(pins,pin) (pins & pin) // test for port pin
#define bit_test(byte,bit) (byte & (1 << bit)) // test for bit set
#define position_delay() _delay_ms(1000)

#define PWM_port PORTA
#define PWM_pin (1 << PA6)
#define PWM_direction DDRA

int main(void) {
   //
   // main
   //
   // set clock divider to /1
   //
   CLKPR = (1 << CLKPCE);
   CLKPR = (0 << CLKPS3) | (0 << CLKPS2) | (0 << CLKPS1) | (0 << CLKPS0);
   //
   // set up timer 1
   //
   TCCR1A = (1 << COM1A1) | (0 << COM1A0); // clear OC1A on compare match
   TCCR1B = (0 << CS12) | (1 << CS11) | (0 << CS10) | (1 << WGM13); // prescaler /8, phase and frequency correct PWM, ICR1 TOP
   ICR1 = 25000; // 20 ms frequency
   //
   // set PWM pin to output
   //
   clear(PWM_port, PWM_pin);
   output(PWM_direction, PWM_pin);
   //
   // main loop
   //
   while (1) {
      //
      // 1 ms PWM on time
      //
      OCR1A = 1250;
      position_delay();
      //
      // 1.5 ms PWM on time
      //
      OCR1A = 1875;
      position_delay();
      //
      // 2 ms PWM on time
      //
      OCR1A = 2500;
      position_delay();
      }
   }
