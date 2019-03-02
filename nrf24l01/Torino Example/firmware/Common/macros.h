/* macros.h
 * Author: Gianfranco Caputo       Created: 23/03/2016 12:01:57  */

#ifndef MACROS_H_
#define MACROS_H_

#define LOW 0
#define HIGH 1

/***** Configure IO *****/
#define configure_as_input(ddr,pin)					(ddr &= ~pin)			// set port direction for input
#define configure_as_output(ddr,pin)				(ddr |= pin)			// set port direction for output

/***** Manipulate Outputs *****/
#define set_high(port,pin)							(port |= pin)			// set port pin
#define set_low(port,pin)							(port &= (~pin))		// clear port pin
#define toggle(port, pin)							(port ^= pin)

/***** Enable interrupt pin change *****/
#define enable_pin_change_interrupt(pcmsk, pin)		(pcmsk |= pin)

/***** Enable specific interrupt *****/
#define enable_interrupt(pcicr, pin)				(pcicr |= pin)

/***** Test Inputs *****/
#define is_high(pins,pin)							(pins & pin)			// test for pin value
#define is_low(pins,pin)							(!(pins & pin))			// test for pin value

/***** Bitwise tests *****/
#define pin_test(port, pin)							(port & pin)			// test for pin set in port
#define bit_test(byte,bit)							(byte & (1 << bit))		// test for bit set in byte

#endif /* MACROS_H_ */