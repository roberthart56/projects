#include <avr/io.h>
#include <stdint.h>
#include <util/delay.h>
#include "nrf24L01.h"


uint8_t payload_len;
uint8_t temp;
uint8_t q = 0;
uint8_t data_array[4];
uint8_t tx_address[5] = {0xD7,0xD7,0xD7,0xD7,0xD7};
uint8_t rx_address[5] = {0xE7,0xE7,0xE7,0xE7,0xE7};


int main()
{
    //
    // set clock divider to /1
    //
    CLKPR = (1 << CLKPCE);
    CLKPR = (0 << CLKPS3) | (0 << CLKPS2) | (0 << CLKPS1) | (0 << CLKPS0);
  //
   // initialize output pins
   //
   set(serial_port,serial_pin_out);
   output(serial_direction,serial_pin_out);
   set(CS_port,CS_pin);
   output(CS_direction,CS_pin);
   clear(CE_port,CE_pin);
   output(CE_direction,CE_pin);
   clear(SCK_port,SCK_pin);
   output(SCK_direction,SCK_pin);
   clear(MOSI_port,MOSI_pin);
   output(MOSI_direction,MOSI_pin);
   clear(MISO_direction,MISO_pin);            //set MISO as input


    /* simple greeting message */
    put_string(&serial_port, serial_pin_out,"\r\n> RX device ready\r\n");

    /* init hardware pins */
    nrf24_init();

    /* Channel #2 , payload length: 4 */
    nrf24_config(2,4);

    /* Set the device addresses */
    nrf24_tx_address(tx_address);
    nrf24_rx_address(rx_address);
    //
    // main loop
    //

    while(1)
    {
        if(nrf24_dataReady())
        {
            nrf24_getData(data_array);
            put_char(&serial_port,serial_pin_out,data_array[0]);
            put_char(&serial_port,serial_pin_out,data_array[1]);
            put_char(&serial_port,serial_pin_out,data_array[2]);
            put_char(&serial_port,serial_pin_out,data_array[3]);

        }
    }
}
/* ------------------------------------------------------------------------- */
