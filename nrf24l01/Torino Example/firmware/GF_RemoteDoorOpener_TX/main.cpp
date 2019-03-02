/*
 * GF_RemoteDoorOpener_TX.cpp
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

#define PAYLOAD_LEN		4

uint8_t data_array[PAYLOAD_LEN+1] = "FLT0";

int main(void)
{
	
	// Init Led/Actuators pins
	set_high(LED_PORT, LED);
	configure_as_output(LED_DDR, LED);
	configure_as_output(LAMP_DDR, LAMP);
	
	// Set the SPI Driver
	Mirf.spi = &MirfSoftwareSpi; 
	
	// Init SPI/ce,csn pins
	Mirf.init();

	// Configure receiving address
	Mirf.setRADDR((uint8_t *)"clie1");
  
	// Set the payload length to sizeof(unsigned long)
	// NB: payload on client and server must be the same
	Mirf.payload = PAYLOAD_LEN;
	
	// Write channel and payload config then power up receiver
	Mirf.config();
	
	set_low(LED_PORT, LED);
	
    /* Replace with your application code */
    while (1) 
    {
		// Set Send Address
		Mirf.setTADDR((uint8_t *)"serv1");
		
		set_high(LAMP_PORT, LAMP);
		// Send data
		Mirf.send((uint8_t *)data_array);
		
		while(Mirf.isSending()){
			;
		}
		
		set_low(LAMP_PORT, LAMP);
		
		_delay_ms(1000);
    }
}

