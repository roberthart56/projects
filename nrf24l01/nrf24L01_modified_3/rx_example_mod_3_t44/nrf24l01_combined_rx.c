/*
* ----------------------------------------------------------------------------
* “THE COFFEEWARE LICENSE” (Revision 1):
* <ihsan@kehribar.me> wrote this file. As long as you retain this notice you
* can do whatever you want with this stuff. If we meet some day, and you think
* this stuff is worth it, you can buy me a coffee in return.
* -----------------------------------------------------------------------------
*/

#include <avr/io.h>
#include <stdint.h>
#include <util/delay.h>

//
//macros from radioPins file.
//

#define set_bit(reg,bit) reg |= (1<<bit)
#define clr_bit(reg,bit) reg &= ~(1<<bit)
#define check_bit(reg,bit) (reg&(1<<bit))



//
// macros
//
#define output(directions,pin) (directions |= pin) // set port direction for output
#define set(port,pin) (port |= pin) // set port pin
#define clear(port,pin) (port &= (~pin)) // clear port pin
#define pin_test(pins,pin) (pins & pin) // test for port pin
#define bit_test(byte,bit) (byte & (1 << bit)) // test for bit set
#define bit_delay_time 102 // bit delay in us for 9600 with overhead at 8 MHz
#define bit_delay() _delay_us(bit_delay_time) // RS232 bit delay
#define half_bit_delay() _delay_us(bit_delay_time/2) // RS232 half bit delay
#define char_delay() _delay_ms(10) // char delay
#define SPI_delay() _delay_us(1) // SPI delay
//
// define serial
//
#define serial_port PORTA
#define serial_direction DDRA
#define serial_pins PINA
//#define serial_pin_in (1 << PA2)
#define serial_pin_out (1 << PA3)
//
// define pins
//
#define CE_port PORTB
#define CE_direction DDRB
#define CE_pin (1 << PB2)
#define CS_port PORTA
#define CS_direction DDRA
#define CS_pin (1 << PA7)
#define SCK_port PORTB
#define SCK_direction DDRB
#define SCK_pin (1 << PB0)
#define MOSI_port PORTB
#define MOSI_direction DDRB
#define MOSI_pin (1 << PB1)
#define MISO_pins PINA
#define MISO_direction DDRA
#define MISO_pin (1 << PA0)
#define IRQ_pins PINA
#define IRQ_direction DDRA
#define IRQ_pin (1 << PA1)
/*
Things defined in nrf24LO1.h
*/
/* Memory Map */
#define CONFIG      0x00
#define EN_AA       0x01
#define EN_RXADDR   0x02
#define SETUP_AW    0x03
#define SETUP_RETR  0x04
#define RF_CH       0x05
#define RF_SETUP    0x06
#define STATUS      0x07
#define OBSERVE_TX  0x08
#define CD          0x09
#define RX_ADDR_P0  0x0A
#define RX_ADDR_P1  0x0B
#define RX_ADDR_P2  0x0C
#define RX_ADDR_P3  0x0D
#define RX_ADDR_P4  0x0E
#define RX_ADDR_P5  0x0F
#define TX_ADDR     0x10
#define RX_PW_P0    0x11
#define RX_PW_P1    0x12
#define RX_PW_P2    0x13
#define RX_PW_P3    0x14
#define RX_PW_P4    0x15
#define RX_PW_P5    0x16
#define FIFO_STATUS 0x17
#define DYNPD       0x1C

/* Bit Mnemonics */

/* configuratio nregister */
#define MASK_RX_DR  6
#define MASK_TX_DS  5
#define MASK_MAX_RT 4
#define EN_CRC      3
#define CRCO        2
#define PWR_UP      1
#define PRIM_RX     0

/* enable auto acknowledgment */
#define ENAA_P5     5
#define ENAA_P4     4
#define ENAA_P3     3
#define ENAA_P2     2
#define ENAA_P1     1
#define ENAA_P0     0

/* enable rx addresses */
#define ERX_P5      5
#define ERX_P4      4
#define ERX_P3      3
#define ERX_P2      2
#define ERX_P1      1
#define ERX_P0      0

/* setup of address width */
#define AW          0 /* 2 bits */

/* setup of auto re-transmission */
#define ARD         4 /* 4 bits */
#define ARC         0 /* 4 bits */

/* RF setup register */
#define PLL_LOCK    4
#define RF_DR       3
#define RF_PWR      1 /* 2 bits */

/* general status register */
#define RX_DR       6
#define TX_DS       5
#define MAX_RT      4
#define RX_P_NO     1 /* 3 bits */
#define TX_FULL     0

/* transmit observe register */
#define PLOS_CNT    4 /* 4 bits */
#define ARC_CNT     0 /* 4 bits */

/* fifo status */
#define TX_REUSE    6
#define FIFO_FULL   5
#define TX_EMPTY    4
#define RX_FULL     1
#define RX_EMPTY    0

/* dynamic length */
#define DPL_P0      0
#define DPL_P1      1
#define DPL_P2      2
#define DPL_P3      3
#define DPL_P4      4
#define DPL_P5      5

/* Instruction Mnemonics */
#define R_REGISTER    0x00 /* last 4 bits will indicate reg. address */
#define W_REGISTER    0x20 /* last 4 bits will indicate reg. address */
#define REGISTER_MASK 0x1F
#define R_RX_PAYLOAD  0x61
#define W_TX_PAYLOAD  0xA0
#define FLUSH_TX      0xE1
#define FLUSH_RX      0xE2
#define REUSE_TX_PL   0xE3
#define ACTIVATE      0x50
#define R_RX_PL_WID   0x60
#define NOP           0xFF
//
// end of nrf24L01 definitions.
//


/*
Things defined in nrf24.h
*/
//#ifndef NRF24
//#define NRF24

#define LOW 0
#define HIGH 1

#define nrf24_ADDR_LEN 5
#define nrf24_CONFIG ((1<<EN_CRC)|(0<<CRCO))

#define NRF24_TRANSMISSON_OK 0
#define NRF24_MESSAGE_LOST   1

//
// end of stuff from nrf24.h
//

/*
functions from nrf24.c
*/

uint8_t payload_len;
uint8_t temp;
uint8_t q = 0;
uint8_t data_array[4];
uint8_t tx_address[5] = {0xD7,0xD7,0xD7,0xD7,0xD7};
uint8_t rx_address[5] = {0xE7,0xE7,0xE7,0xE7,0xE7};
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
/* ------------------------------------------------------------------------- */
/*
Functions defined in radioPin function to set and clear.
*/
/* ------------------------------------------------------------------------- */
void nrf24_ce_digitalWrite(uint8_t state)
{
    if(state)
    {
        set_bit(PORTB,2);
    }
    else
    {
        clr_bit(PORTB,2);
    }
}
/* ------------------------------------------------------------------------- */
void nrf24_csn_digitalWrite(uint8_t state)
{
    if(state)
    {
        set_bit(PORTA,7);
    }
    else
    {
        clr_bit(PORTA,7);
    }
}
/* ------------------------------------------------------------------------- */
void nrf24_sck_digitalWrite(uint8_t state)
{
    if(state)
    {
        set_bit(PORTB,0);
    }
    else
    {
        clr_bit(PORTB,0);
    }
}
/* ------------------------------------------------------------------------- */
void nrf24_mosi_digitalWrite(uint8_t state)
{
    if(state)
    {
        set_bit(PORTB,1);
    }
    else
    {
        clr_bit(PORTB,1);
    }
}
/* ------------------------------------------------------------------------- */
uint8_t nrf24_miso_digitalRead()
{
    return check_bit(PINA,0);
}
/* ------------------------------------------------------------------------- */

/*
Functions defined in radioPin function to set and clear.
*/

//
//Start of low level functions
//

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
    nrf24_csn_digitalWrite(LOW);
    spi_transfer(W_REGISTER | (REGISTER_MASK & reg));
    spi_transfer(value);
    nrf24_csn_digitalWrite(HIGH);
}

/* Read single register from nrf24 */
void nrf24_readRegister(uint8_t reg, uint8_t* value, uint8_t len)
{
    nrf24_csn_digitalWrite(LOW);
    spi_transfer(R_REGISTER | (REGISTER_MASK & reg));
    nrf24_transferSync(value,value,len);
    nrf24_csn_digitalWrite(HIGH);
}

/* Write to a single register of nrf24 */
void nrf24_writeRegister(uint8_t reg, uint8_t* value, uint8_t len)
{
    nrf24_csn_digitalWrite(LOW);
    spi_transfer(W_REGISTER | (REGISTER_MASK & reg));
    nrf24_transmitSync(value,len);
    nrf24_csn_digitalWrite(HIGH);
}

//
//end of low level functions
//

//
//second level functions
//

void nrf24_powerUpRx()
{
    nrf24_csn_digitalWrite(LOW);
    spi_transfer(FLUSH_RX);
    nrf24_csn_digitalWrite(HIGH);

    nrf24_configRegister(STATUS,(1<<RX_DR)|(1<<TX_DS)|(1<<MAX_RT));

    nrf24_ce_digitalWrite(LOW);
    nrf24_configRegister(CONFIG,nrf24_CONFIG|((1<<PWR_UP)|(1<<PRIM_RX)));
    nrf24_ce_digitalWrite(HIGH);
}

void nrf24_powerUpTx()
{
    nrf24_configRegister(STATUS,(1<<RX_DR)|(1<<TX_DS)|(1<<MAX_RT));

    nrf24_configRegister(CONFIG,nrf24_CONFIG|((1<<PWR_UP)|(0<<PRIM_RX)));
}

void nrf24_powerDown()
{
    nrf24_ce_digitalWrite(LOW);
    nrf24_configRegister(CONFIG,nrf24_CONFIG);
}

//
//end of second level functions
//


/* init the hardware pins */
void nrf24_init()
{
    //nrf24_setupPins();
    nrf24_ce_digitalWrite(LOW);
    nrf24_csn_digitalWrite(HIGH);
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
    nrf24_ce_digitalWrite(LOW);
    nrf24_writeRegister(RX_ADDR_P1,adr,nrf24_ADDR_LEN);
    nrf24_ce_digitalWrite(HIGH);
}

/* Returns the payload length */
uint8_t nrf24_payload_length()
{
    return payload_len;
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
    nrf24_csn_digitalWrite(LOW);
    rv = spi_transfer(NOP);
    nrf24_csn_digitalWrite(HIGH);
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


/* Returns the length of data waiting in the RX fifo */
uint8_t nrf24_payloadLength()
{
    uint8_t status;
    nrf24_csn_digitalWrite(LOW);
    spi_transfer(R_RX_PL_WID);
    status = spi_transfer(0x00);
    nrf24_csn_digitalWrite(HIGH);
    return status;
}

/* Reads payload bytes into data array */
void nrf24_getData(uint8_t* data)
{
    /* Pull down chip select */
    nrf24_csn_digitalWrite(LOW);

    /* Send cmd to read rx payload */
    spi_transfer( R_RX_PAYLOAD );

    /* Read payload */
    nrf24_transferSync(data,data,payload_len);

    /* Pull up chip select */
    nrf24_csn_digitalWrite(HIGH);

    /* Reset status register */
    nrf24_configRegister(STATUS,(1<<RX_DR));
}

/* Returns the number of retransmissions occured for the last message */
uint8_t nrf24_retransmissionCount()
{
    uint8_t rv;
    nrf24_readRegister(OBSERVE_TX,&rv,1);
    rv = rv & 0x0F;
    return rv;
}

// Sends a data package to the default address. Be sure to send the correct
// amount of bytes as configured as payload on the receiver.
void nrf24_send(uint8_t* value)
{
    /* Go to Standby-I first */
    nrf24_ce_digitalWrite(LOW);

    /* Set to transmitter mode , Power up if needed */
    nrf24_powerUpTx();

    /* Do we really need to flush TX fifo each time ? */
    #if 1
        /* Pull down chip select */
        nrf24_csn_digitalWrite(LOW);

        /* Write cmd to flush transmit FIFO */
        spi_transfer(FLUSH_TX);

        /* Pull up chip select */
        nrf24_csn_digitalWrite(HIGH);
    #endif

    /* Pull down chip select */
    nrf24_csn_digitalWrite(LOW);

    /* Write cmd to write payload */
    spi_transfer(W_TX_PAYLOAD);

    /* Write payload */
    nrf24_transmitSync(value,payload_len);

    /* Pull up chip select */
    nrf24_csn_digitalWrite(HIGH);

    /* Start the transmission */
    nrf24_ce_digitalWrite(HIGH);
}



uint8_t nrf24_isSending()
{
    uint8_t status;

    /* read the current status */
    status = nrf24_getStatus();

    /* if sending successful (TX_DS) or max retries exceded (MAX_RT). */
    if((status & ((1 << TX_DS)  | (1 << MAX_RT))))
    {
        return 0; /* false */
    }

    return 1; /* true */

}



uint8_t nrf24_lastMessageStatus()
{
    uint8_t rv;

    rv = nrf24_getStatus();

    /* Transmission went OK */
    if((rv & ((1 << TX_DS))))
    {
        return NRF24_TRANSMISSON_OK;
    }
    /* Maximum retransmission count is reached */
    /* Last message probably went missing ... */
    else if((rv & ((1 << MAX_RT))))
    {
        return NRF24_MESSAGE_LOST;
    }
    /* Probably still sending ... */
    else
    {
        return 0xFF;
    }
}


//
//end of functions from nrf24.c
//






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
