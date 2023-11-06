#include "nrf24L01.h"
/*
functions from nrf24.c
*/
/* ------------------------------------------------------------------------- */

/* ------------------------------------------------------------------------- */
/* Printing functions */
/* ------------------------------------------------------------------------- */
//
// put_char
//    send character in txchar on port pin
//    assumes line driver (inverts bits)
//
void put_char(volatile unsigned char *port, unsigned char pin, char txchar) {
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

   void put_string(volatile unsigned char *port, unsigned char pin, char *str) {
      //
      // print a null-terminated string
      //
      static int index;
      index = 0;
      do {
         put_char(port, pin, str[index]);
         ++index;
         } while (str[index] != 0);
      }

//
//Start of low level functions
//

/* software spi routine */
uint8_t spi_transfer(uint8_t tx)
{
    uint8_t i = 0;
    uint8_t rx = 0;

    clear(SCK_port, SCK_pin);

    for(i=0;i<8;i++)
    {

        if(tx & (1<<(7-i)))
        {
            set(MOSI_port, MOSI_pin);
        }
        else
        {
            clear(MOSI_port, MOSI_pin);
        }

        set(SCK_port, SCK_pin);

        rx = rx << 1;
        if(pin_test(MISO_pins, MISO_pin))
        {
            rx |= 0x01;
        }

        clear(SCK_port, SCK_pin);

    }

    return rx;
}

/* send and receive multiple bytes over SPI */
void nrf24_transferSync(uint8_t* dataout,uint8_t* datain,uint8_t len)
{
    uint8_t i;

    for(i=0;i<len;i++)
    {
        datain[i] = spi_transfer(dataout[i]);
    }

}

/* send multiple bytes over SPI */
void nrf24_transmitSync(uint8_t* dataout,uint8_t len)
{
    uint8_t i;

    for(i=0;i<len;i++)
    {
        spi_transfer(dataout[i]);
    }

}

/* Clocks only one byte into the given nrf24 register */
void nrf24_configRegister(uint8_t reg, uint8_t value)
{
    clear(CS_port, CS_pin);
    spi_transfer(W_REGISTER | (REGISTER_MASK & reg));
    spi_transfer(value);
    set(CS_port, CS_pin);
}

/* Read single register from nrf24 */
void nrf24_readRegister(uint8_t reg, uint8_t* value, uint8_t len)
{
    clear(CS_port, CS_pin);
    spi_transfer(R_REGISTER | (REGISTER_MASK & reg));
    nrf24_transferSync(value,value,len);
    set(CS_port, CS_pin);
}

/* Write to a single register of nrf24 */
void nrf24_writeRegister(uint8_t reg, uint8_t* value, uint8_t len)
{
    clear(CS_port, CS_pin);
    spi_transfer(W_REGISTER | (REGISTER_MASK & reg));
    nrf24_transmitSync(value,len);
    set(CS_port, CS_pin);
}

//
//end of low level functions
//

//
//second level functions
//

void nrf24_powerUpRx()
{
    clear(CS_port, CS_pin);
    spi_transfer(FLUSH_RX);
    set(CS_port, CS_pin);

    nrf24_configRegister(STATUS,(1<<RX_DR)|(1<<TX_DS)|(1<<MAX_RT));

    clear(CE_port, CE_pin);
    nrf24_configRegister(CONFIG,nrf24_CONFIG|((1<<PWR_UP)|(1<<PRIM_RX)));
    set(CE_port, CE_pin);
}


void nrf24_powerDown()
{
    clear(CE_port, CE_pin);
    nrf24_configRegister(CONFIG,nrf24_CONFIG);
}

//
//end of second level functions
//


/* init the hardware pins */
void nrf24_init()
{
    //nrf24_setupPins();
    clear(CE_port, CE_pin);
    set(CS_port, CS_pin);
}

/* configure the module */
void nrf24_config(uint8_t channel, uint8_t pay_length)
{
    /* Use static payload length ... */
    payload_len = pay_length;

    // Set RF channel
    nrf24_configRegister(RF_CH,channel);

    // Set length of incoming payload
    nrf24_configRegister(RX_PW_P0, 0x00); // Auto-ACK pipe ...
    nrf24_configRegister(RX_PW_P1, payload_len); // Data payload pipe
    nrf24_configRegister(RX_PW_P2, 0x00); // Pipe not used
    nrf24_configRegister(RX_PW_P3, 0x00); // Pipe not used
    nrf24_configRegister(RX_PW_P4, 0x00); // Pipe not used
    nrf24_configRegister(RX_PW_P5, 0x00); // Pipe not used

    // 1 Mbps, TX gain: 0dbm
    nrf24_configRegister(RF_SETUP, (0<<RF_DR)|((0x03)<<RF_PWR));

    // CRC enable, 1 byte CRC length
    nrf24_configRegister(CONFIG,nrf24_CONFIG);

    // Auto Acknowledgment
    nrf24_configRegister(EN_AA,(1<<ENAA_P0)|(1<<ENAA_P1)|(0<<ENAA_P2)|(0<<ENAA_P3)|(0<<ENAA_P4)|(0<<ENAA_P5));

    // Enable RX addresses
    nrf24_configRegister(EN_RXADDR,(1<<ERX_P0)|(1<<ERX_P1)|(0<<ERX_P2)|(0<<ERX_P3)|(0<<ERX_P4)|(0<<ERX_P5));

    // Auto retransmit delay: 1000 us and Up to 15 retransmit trials
    nrf24_configRegister(SETUP_RETR,(0x04<<ARD)|(0x0F<<ARC));

    // Dynamic length configurations: No dynamic length
    nrf24_configRegister(DYNPD,(0<<DPL_P0)|(0<<DPL_P1)|(0<<DPL_P2)|(0<<DPL_P3)|(0<<DPL_P4)|(0<<DPL_P5));

    // Start listening
    nrf24_powerUpRx();
}

/* Set the RX address */
void nrf24_rx_address(uint8_t * adr)
{
    clear(CE_port, CE_pin);
    nrf24_writeRegister(RX_ADDR_P1,adr,nrf24_ADDR_LEN);
    set(CE_port, CE_pin);
}


/* Set the TX address */
void nrf24_tx_address(uint8_t* adr)
{
    /* RX_ADDR_P0 must be set to the sending addr for auto ack to work. */
    nrf24_writeRegister(RX_ADDR_P0,adr,nrf24_ADDR_LEN);
    nrf24_writeRegister(TX_ADDR,adr,nrf24_ADDR_LEN);
}

uint8_t nrf24_getStatus()
{
    uint8_t rv;
    clear(CS_port, CS_pin);
    rv = spi_transfer(NOP);
    set(CS_port, CS_pin);
    return rv;
}


/* Checks if receive FIFO is empty or not */
uint8_t nrf24_rxFifoEmpty()
{
    uint8_t fifoStatus;

    nrf24_readRegister(FIFO_STATUS,&fifoStatus,1);

    return (fifoStatus & (1 << RX_EMPTY));
}

/* Checks if data is available for reading */
/* Returns 1 if data is ready ... */
uint8_t nrf24_dataReady()
{
    // See note in getData() function - just checking RX_DR isn't good enough
    uint8_t status = nrf24_getStatus();

    // We can short circuit on RX_DR, but if it's not set, we still need
    // to check the FIFO for any pending packets
    if ( status & (1 << RX_DR) )
    {
        return 1;
    }

    return !nrf24_rxFifoEmpty();;
}



/* Reads payload bytes into data array */
void nrf24_getData(uint8_t* data)
{
    /* Pull down chip select */
    clear(CS_port, CS_pin);

    /* Send cmd to read rx payload */
    spi_transfer( R_RX_PAYLOAD );

    /* Read payload */
    nrf24_transferSync(data,data,payload_len);

    /* Pull up chip select */
    set(CS_port, CS_pin);

    /* Reset status register */
    nrf24_configRegister(STATUS,(1<<RX_DR));
}
