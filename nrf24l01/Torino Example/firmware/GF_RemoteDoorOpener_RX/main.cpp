/*
 * GF_RemoteDoorOpener_RX.cpp
 *
 * Created: 16/05/2016 23:24:35
 * Author : Shad0w
 */ 

#include <avr/io.h>
#include <util/delay.h>
#include <Mirf.h>
#include <nRF24L01.h>
#include <MirfSoftwareSpiDriver.h>
#include "config.h"
#include "macros.h"

#define ACTUATOR_DELAY	2000
#define PAYLOAD_LEN		4

uint8_t data[PAYLOAD_LEN];

int main(void)
{
	// Init Led/Actuators pins
	configure_as_output(LED_DDR, LED);
	configure_as_output(OUT_DDR, (OUT1 | OUT2));
	
	// Set the SPI Driver
	Mirf.spi = &MirfSoftwareSpi; 
	
	// Init SPI/ce,csn pins
	Mirf.init();

	// Configure receiving address
	Mirf.setRADDR((uint8_t *)"serv1");
  
	// Set the payload length to sizeof(unsigned long)
	// NB: payload on client and server must be the same
	Mirf.payload = PAYLOAD_LEN;
	
	// Write channel and payload config then power up receiver
	Mirf.config();
	
    /* Replace with your application code */
    while (1) 
    {
		// If a packet has been received
		if(Mirf.dataReady()) {
			set_high(LED_PORT, LED);
			
			// Get packet payload into 'data' buffer
			Mirf.getData(data);
			
			if(data[0] == 'F' && data[1] == 'L' && data[2] == 'T')
			{
				// Open the door, actuating out pins
				set_high(OUT_PORT, (OUT1 | OUT2));
				
				_delay_ms(ACTUATOR_DELAY);
				
				set_low(OUT_PORT, (OUT1 | OUT2));
				set_low(LED_PORT, LED);
				
			}
			else {
				_delay_ms(100);
				set_low(LED_PORT, LED);
			}
		}
    }
}

