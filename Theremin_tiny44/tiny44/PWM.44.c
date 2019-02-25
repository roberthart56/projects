

#include <avr/io.h>
#include <util/delay.h>

#define output(directions,pin) (directions |= pin) // set port direction for output
#define set(port,pin) (port |= pin) // set port pin
#define clear(port,pin) (port &= (~pin)) // clear port pin
#define pin_test(pins,pin) (pins & pin) // test for port pin
#define bit_test(byte,bit) (byte & (1 << bit)) // test for bit set
#define position_delay() _delay_ms(1000)

#define PWM1_port PORTA
#define PWM1_pin (1 << PA6)
#define PWM1_direction DDRA

#define PWM2_port PORTB
#define PWM2_pin (1 << PB2)
#define PWM2_direction DDRB

int main(void) {
   //
   // main
   //
   // set clock divider to /1
   //
   CLKPR = (1 << CLKPCE);
   CLKPR = (0 << CLKPS3) | (0 << CLKPS2) | (0 << CLKPS1) | (0 << CLKPS0);
   //
   // set up timer 1 (16 bit timer)  Use this one for variable frequency 100Hz to max frequency. output on 0C1A (PA6, pin 7).
   //Fast PWM with toggle to get variable frequency with 50 Percent duty cycle.
   //
   TCCR1A = (0 << COM1A1) | (1 << COM1A0)| (1 << WGM11)| (1 << WGM10); // toggle OC1A on compare match
   TCCR1B = (1 << WGM13) | (1 << WGM12) | (0 << CS12) | (0 << CS11) | (1 << CS10) ;  // no prescaler, Fast PWM, ICR1 TOP.
   //ICR1 = 40000; //(prescaler 1) x (1/8 microsecond) x (2) x (40000) =  10 msec period gives minimum frequency of 100 Hz.
   OCR1A = 40000;
   //
   // set up timer 0  Use this one in Fast PWM mode for  variable duty cycle PWM on 0C0A (PB2, pin 5) at 31 KHz.
   //
   TCCR0A = (1 << COM0A1) | (0 << COM0A0)| (1 << WGM01)| (1 << WGM00); //   Set 0C0A at bottom, clear 0C0A on compare match.
   TCCR0B = (0 << WGM02) | (0 << CS02) | 0 << (CS01) | (1 << CS00); // no prescaler, fast PWM.  Top at 0xFF.
    //(prescaler 1) x (1/8 microsecond)  x (256) =  32 microsecond period. Gives frequency of 31 kHz.
   OCR0A = 127; //50% duty cycle.

   uint16_t count = 0 ;

   //
   // set PWM pin to output
   //
   clear(PWM1_port, PWM1_pin);
   output(PWM1_direction, PWM1_pin);

   clear(PWM2_port, PWM2_pin);
   output(PWM2_direction, PWM2_pin);
   //
   // main loop
   //
   while (1) {

      for (count = 400; count<40000; count++){
        OCR1A = count;
        OCR0A += 1;
        _delay_ms(1);
      }
    }
   }
