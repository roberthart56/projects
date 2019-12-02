// Shamelessly copied and moDIfied from Neil Gershenfeld's code by Rob Hart for purposes of instruction.
//
//
// Button  PA4 (pin 9).  
// LED     PA3 (pin 10).  
#include <avr/io.h>

#define output(directions,pin) (directions |= pin) // set port direction for output
#define input(directions,pin) (directions &= (~pin)) // set port direction for input
#define set(port,pin) (port |= pin) // set port pin
#define clear(port,pin) (port &= (~pin)) // clear port pin
#define pin_test(pins,pin) (pins & pin) // test for port pin
#define bit_test(byte,bit) (byte & (1 << bit)) // test for bit set

#define input_port PORTA		// The button is on port A
#define input_direction DDRA	//  DDRA defines input/output for port A
#define input_pin (1 << PA4)	//  The button is on pin 4 of port A
#define input_pins PINA			//  PINA is the register that is read to detect input high or low.
#define output_port PORTA		//  port A will be used for the LED
#define output_direction DDRA	//  Direction port for LED
#define output_pin (1 << PA3)	// LED ON PA3 (PHYSICAL PIN 10)


int main(void) {
   //
   // main
   //
   
   // initialize pins
   //
   output(output_direction, output_pin);
   set(input_port, input_pin); // turn on pull-up
   input(input_direction, input_pin);
   //
   // main loop
   //
   while (1) {
      //
      // 
      //
      if (pin_test(input_pins,input_pin))
      	clear(output_port,output_pin);
	  else
		  set(output_port,output_pin);
      //
      // wait for button up
      //
      
      }
   }
