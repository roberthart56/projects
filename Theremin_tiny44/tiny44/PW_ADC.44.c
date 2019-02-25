

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
#define position_delay() _delay_ms(1000)
#define char_delay() _delay_ms(20) // char delay

#define serial_port PORTA
#define serial_direction DDRA
#define serial_pin_out (1 << PA4)

#define PWM1_port PORTA
#define PWM1_pin (1 << PA6)
#define PWM1_direction DDRA

#define PWM2_port PORTB
#define PWM2_pin (1 << PB2)
#define PWM2_direction DDRB

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
   // set clock divider to /1
   //
   CLKPR = (1 << CLKPCE);
   CLKPR = (0 << CLKPS3) | (0 << CLKPS2) | (0 << CLKPS1) | (0 << CLKPS0);

   //
   // init A/D
   //
   //analog inputs on PA0(ADC0, 13) and PA1(ADC1, 12).
   ADMUX = (0 << REFS1) | (0 << REFS0) // Vcc ref
      | (0 << MUX5)| (0 << MUX4)| (0 << MUX3) | (0 << MUX2) | (0 << MUX1) | (0 << MUX0); // ADC0 single ended.  (1 << MUX0) for ADC1
   ADCSRA = (1 << ADEN) // enable
      | (1 << ADPS2) | (1 << ADPS1) | (1 << ADPS0); // prescaler /128
    ADCSRB = (0 << ADLAR);


   //
   // set up timer 1 (16 bit timer)  Use this one for variable frequency 100Hz to max frequency. output on 0C1A (PA6, pin 7).
   //Fast PWM with toggle to get variable frequency with 50 Percent duty cycle.
   //
   TCCR1A = (0 << COM1A1) | (1 << COM1A0)| (1 << WGM11)| (1 << WGM10); // toggle OC1A on compare match
   TCCR1B = (1 << WGM13) | (1 << WGM12) | (0 << CS12) | (0 << CS11) | (1 << CS10) ;  // no prescaler, Fast PWM, OCR1A TOP.
   OCR1A = 40000;//(prescaler 1) x (1/8 microsecond) x (2) x (40000) =  10 msec period gives minimum frequency of 100 Hz.

   //
   // set up timer 0  Use this one in Fast PWM mode for  variable duty cycle PWM on 0C0A (PB2, pin 5) at 31 KHz.
   //
   TCCR0A = (1 << COM0A1) | (0 << COM0A0)| (1 << WGM01)| (1 << WGM00); //   Set 0C0A at bottom, clear 0C0A on compare match.
   TCCR0B = (0 << WGM02) | (0 << CS02) | 0 << (CS01) | (1 << CS00); // no prescaler, fast PWM.  Top at 0xFF.
    //(prescaler 1) x (1/8 microsecond)  x (256) =  32 microsecond period. Gives frequency of 31 kHz.
   OCR0A = 127; //50% duty cycle.

   //uint16_t count = 0 ;

   //
   // set PWM pin to output
   //

   set(serial_port, serial_pin_out);
   output(serial_direction, serial_pin_out);

   clear(PWM1_port, PWM1_pin);
   output(PWM1_direction, PWM1_pin);

   clear(PWM2_port, PWM2_pin);
   output(PWM2_direction, PWM2_pin);
   //
   // main loop
   //
   while (1) {
     //Set multiplex as needed to switch between ADC0 and ADC1.
     //
     ADMUX =(0 << REFS1) | (0 << REFS0)| (0 << MUX5)| (0 << MUX4)| (0 << MUX3) | (0 << MUX2) | (0 << MUX1) | (0 << MUX0); // ADC0 single ended.  (1 << MUX0) for ADC1
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
     // use result to change period.
     //


     OCR1A = 40 * ADC; // should range from 0 - ~40000

     //put_char(&serial_port, serial_pin_out, (signal_1 & 255));
     //char_delay();

     //Set multiplex as needed to switch between ADC0 and ADC1.
     //
     ADMUX =(0 << REFS1) | (0 << REFS0)| (0 << MUX5)| (0 << MUX4)| (0 << MUX3) | (0 << MUX2) | (0 << MUX1) | (1 << MUX0); // (1 << MUX0) for ADC1 single ended
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
     // use result to change duty cycle.
     //
     OCR0A = ADC/4 ;//(ADC >> 2) & 255; // should range from 0 - 255

     put_char(&serial_port, serial_pin_out, OCR0A);
     char_delay();

      _delay_ms(100);  // update infrequently so that waveform is stable.

    }
   }
