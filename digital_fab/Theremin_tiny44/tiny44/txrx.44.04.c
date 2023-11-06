//
// hello.txrx.45.c
//
// step response transmit-receive hello-world
//    9600 baud FTDI interface
//
// Neil Gershenfeld
// 11/6/11
//
// (c) Massachusetts Institute of Technology 2011
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
#define bit_delay_time 102 // bit delay for 9600 with overhead
#define bit_delay() _delay_us(bit_delay_time) // RS232 bit delay
#define half_bit_delay() _delay_us(bit_delay_time/2) // RS232 half bit delay
#define settle_delay() _delay_us(100) // settle delay
-
#define motor_delay() _delay_us(20) //unit delay for motor on loop.
#define nloop 100 // loops to accumulate

#define serial_port PORTA
#define serial_direction DDRA
#define serial_pin_out (1 << PA5)
#define transmit_port PORTB
#define transmit_direction DDRB
#define transmit_pin (1 << PB2)

//in1 is PA3, in2 is PA2
#define motor_port PORTA
#define motor_direction DDRA
#define in1_pin (1 << PA3)
#define in2_pin (1 << PA2)


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
   //
   // char delay
   //
   bit_delay();
   }

int main(void) {
   //
   // main
   //
   static unsigned char count;
   static uint32_t up,down,signal_1,signal_2;
   static uint32_t min_1, max_1, min_2, max_2, setpoint, deviation, count_2;
   min_1 = 7600;
   max_1 = 16000;
   min_2 = 6400;
   max_2 = 9300;


   //
   // set clock divider to /1
   //
   CLKPR = (1 << CLKPCE);
   CLKPR = (0 << CLKPS3) | (0 << CLKPS2) | (0 << CLKPS1) | (0 << CLKPS0);
   //
   // initialize output pins
   //
   set(serial_port, serial_pin_out);
   output(serial_direction, serial_pin_out);
   clear(transmit_port, transmit_pin);
   output(transmit_direction, transmit_pin);
   output(motor_direction, in1_pin);
   output(motor_direction, in2_pin);



   //
   // init A/D  ORIGINAL FOR T45.  Change to reflect slightly different bits for t44.
   //

   ADCSRA = (1 << ADEN) // enable
      | (1 << ADPS2) | (1 << ADPS1) | (1 << ADPS0); // prescaler /128
   ADCSRB =  (0 << ADLAR); // right adjust (not really necessary - this is the default.)

   //
   // main loop
   //
   while (1) {
     clear(motor_port, in1_pin);
     clear(motor_port, in2_pin);
     //
     //Set multiplexer for PB6 - linear sensor.
     //
      ADMUX = (0 << REFS1) | (0 << REFS0) // Vcc ref
          | (0 << MUX5) | (0 << MUX4) | (0 << MUX3) | (1 << MUX2) | (1 << MUX1) | (1 << MUX0); // PA7 (pin 6) on right side, rx1
      //
      //
      // accumulate
      //
      up = 0;
      down = 0;
      for (count = 0; count < nloop; ++count) {
         //
         // settle, charge
         //
         settle_delay();
         set(transmit_port, transmit_pin);
         //
         // initiate conversion
         //
         ADCSRA |= (1 << ADSC);
         //
         // wait for completion
         //
         while (ADCSRA & (1 << ADSC))
            ;
         //
         // save result
         //
         up += ADC;
         //
         // settle, discharge
         //
         settle_delay();
         clear(transmit_port, transmit_pin);
         //
         // initiate conversion
         //
         ADCSRA |= (1 << ADSC);
         //
         // wait for completion
         //
         while (ADCSRA & (1 << ADSC))
            ;
         //
         // save result
         //
         down += ADC;
         }

      signal_1 = up - down;


      //
      //Set multiplexer for PB7 - rotary sensor.
      //
       ADMUX = (0 << REFS1) | (0 << REFS0) // Vcc ref
           | (0 << MUX5) | (0 << MUX4) | (0 << MUX3) | (1 << MUX2) | (1 << MUX1) | (0 << MUX0); // PA6 (pin 7), (left side) rx2
       // accumulate
       //
       up = 0;
       down = 0;
       for (count = 0; count < nloop; ++count) {
          //
          // settle, charge
          //
          settle_delay();
          set(transmit_port, transmit_pin);
          //
          // initiate conversion
          //
          ADCSRA |= (1 << ADSC);
          //
          // wait for completion
          //
          while (ADCSRA & (1 << ADSC))
             ;
          //
          // save result
          //
          up += ADC;
          //
          // settle, discharge
          //
          settle_delay();
          clear(transmit_port, transmit_pin);
          //
          // initiate conversion
          //
          ADCSRA |= (1 << ADSC);
          //
          // wait for completion
          //
          while (ADCSRA & (1 << ADSC))
             ;
          //
          // save result
          //
          down += ADC;
          }

       signal_2 = up - down;

       setpoint = min_2 + ((signal_1 - min_1) * (max_2 - min_2))/(max_1 - min_1);


       if (setpoint > signal_2) {
           set(motor_port, in1_pin);
           deviation = setpoint - signal_2;
           //deviation = 5000;
         }

       else {
           deviation = signal_2 - setpoint;
           //deviation = 1000;
           set(motor_port, in2_pin);
         }

       if (deviation > 10000) deviation = 0;

       for (count_2 = 0; count_2 < deviation; ++count_2){
           motor_delay();
         }

/*
      put_char(&serial_port, serial_pin_out, 1);
      char_delay();
      put_char(&serial_port, serial_pin_out, 2);
      char_delay();
      put_char(&serial_port, serial_pin_out, 3);
      char_delay();
      put_char(&serial_port, serial_pin_out, 4);
      char_delay();//


      put_char(&serial_port, serial_pin_out, (signal_1 & 255));
      char_delay();
      put_char(&serial_port, serial_pin_out, ((signal_1 >> 8) & 255));
      char_delay();

      put_char(&serial_port, serial_pin_out, (signal_2 & 255));
      char_delay();
      put_char(&serial_port, serial_pin_out, ((signal_2 >> 8) & 255));
      char_delay();

      put_char(&serial_port, serial_pin_out, (setpoint & 255));
      char_delay();
      put_char(&serial_port, serial_pin_out, ((setpoint >> 8) & 255));
      char_delay();

      put_char(&serial_port, serial_pin_out, (deviation & 255));
      char_delay();
      put_char(&serial_port, serial_pin_out, ((deviation >> 8) & 255));
      char_delay();
*/


      }
   }
