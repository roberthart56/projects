/*
* ----------------------------------------------------------------------------
* “THE COFFEEWARE LICENSE” (Revision 1):
* <ihsan@kehribar.me> wrote this file. As long as you retain this notice you
* can do whatever you want with this stuff. If we meet some day, and you think
* this stuff is worth it, you can buy me a coffee in return.
* -----------------------------------------------------------------------------
* Please define your platform specific functions in this file ...
* -----------------------------------------------------------------------------
*/

#include <avr/io.h>
#include "macros.h"
#include "config.h"

/* ------------------------------------------------------------------------- */
void nrf24_setupPins()
{
	configure_as_output(RF24_DDR, RF24_CE);		// CE output
	configure_as_output(RF24_DDR, RF24_CSN);		// CSN output
	configure_as_output(RF24_DDR, RF24_SCK);		// SCK output
	configure_as_output(RF24_DDR, RF24_MOSI);		// MOSI output
	configure_as_input(RF24_DDR, RF24_MISO);		// MISO input
}
/* ------------------------------------------------------------------------- */
void nrf24_ce_digitalWrite(uint8_t state)
{
    if(state)
    {
        set_high(RF24_PORT,RF24_CE);
    }
    else
    {
        set_low(RF24_PORT,RF24_CE);
    }
}
/* ------------------------------------------------------------------------- */
void nrf24_csn_digitalWrite(uint8_t state)
{
    if(state)
    {
        set_high(RF24_PORT,RF24_CSN);
    }
    else
    {
        set_low(RF24_PORT,RF24_CSN);
    }
}
/* ------------------------------------------------------------------------- */
void nrf24_sck_digitalWrite(uint8_t state)
{
    if(state)
    {
        set_high(RF24_PORT,RF24_SCK);
    }
    else
    {
        set_low(RF24_PORT,RF24_SCK);
    }
}
/* ------------------------------------------------------------------------- */
void nrf24_mosi_digitalWrite(uint8_t state)
{
    if(state)
    {
        set_high(RF24_PORT,RF24_MOSI);
    }
    else
    {
        set_low(RF24_PORT,RF24_MOSI);
    }
}
/* ------------------------------------------------------------------------- */
uint8_t nrf24_miso_digitalRead()
{
    return pin_test(RF24_PIN,RF24_MISO);
}

/* software spi routine */
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
/* ------------------------------------------------------------------------- */
