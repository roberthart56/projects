//
//
// hello.stepper.bipolar.44.full.c
//
// bipolar full stepping hello-world
//
// Neil Gershenfeld
// 11/21/12
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

#define bridge_port PORTA // H-bridge port
#define bridge_direction DDRA // H-bridge direction
#define A2 (1 << PA0) // H-bridge output pins
#define A1 (1 << PA1) // "
#define B2 (1 << PA3) // "
#define B1 (1 << PA4) // "
#define on_delay() _delay_ms(500) // PWM on time
#define off_delay() _delay_ms(500) // PWM off time


int main(void) {
   //
   // main
   //

   //
   // set clock divider to /1
   //
   CLKPR = (1 << CLKPCE);
   CLKPR = (0 << CLKPS3) | (0 << CLKPS2) | (0 << CLKPS1) | (0 << CLKPS0);
   //
   // initialize bridge pins
   //
   clear(bridge_port, A1);
   output(bridge_direction, A1);
   clear(bridge_port, A2);
   output(bridge_direction, A2);
   clear(bridge_port, B1);
   output(bridge_direction, B1);
   clear(bridge_port, B2);
   output(bridge_direction, B2);
   //
   // main loop
   //
   while (1) {
     set(bridge_port, A1);
     set(bridge_port, B1);
      }
   }
