#include <avr/io.h>
#include "config.h"
#include "macros.h"

#include "MirfSoftwareSpiDriver.h"

/*
uint8_t spi_transfer(uint8_t tx)
{
	uint8_t i = 0;
	uint8_t rx = 0;

	nrf24_sck_digitalWrite(LOW);

	for(i=0;i<8;i++)
	{

		if(tx & (1<<(7-i)))
		{
			nrf24_mosi_digitalWrite(HIGH);
		}
		else
		{
			nrf24_mosi_digitalWrite(LOW);
		}

		nrf24_sck_digitalWrite(HIGH);

		rx = rx << 1;
		if(nrf24_miso_digitalRead())
		{
			rx |= 0x01;
		}

		nrf24_sck_digitalWrite(LOW);

	}

	return rx;
}
*/

uint8_t MirfSoftwareSpiDriver::transfer(uint8_t tx){
	uint8_t i = 0;
	uint8_t rx = 0;
	
	sckLo();
	for(i=0;i<8;i++)
	{

		if(tx & (1<<(7-i)))
		{
			mosiHi();
		}
		else
		{
			mosiLo();
		}

		sckHi();

		rx = rx << 1;
		if(getMiso())
		{
			rx |= 0x01;
		}

		sckLo();

	}

	return rx;
}

void MirfSoftwareSpiDriver::begin(){
	configure_as_output(RF24_DDR, RF24_SCK);		// SCK output
	configure_as_output(RF24_DDR, RF24_MOSI);		// MOSI output
	configure_as_input(RF24_DDR, RF24_MISO);		// MISO input
}

void MirfSoftwareSpiDriver::end(){
}

void MirfSoftwareSpiDriver::sckHi() {
	set_high(RF24_PORT,RF24_SCK);
}
void MirfSoftwareSpiDriver::sckLo() {
	set_low(RF24_PORT,RF24_SCK);
}

void MirfSoftwareSpiDriver::mosiHi() {
	set_high(RF24_PORT,RF24_MOSI);
}
void MirfSoftwareSpiDriver::mosiLo() {
	set_low(RF24_PORT,RF24_MOSI);
}

uint8_t MirfSoftwareSpiDriver::getMiso() {
	return pin_test(RF24_PIN,RF24_MISO);
}

MirfSoftwareSpiDriver MirfSoftwareSpi;
