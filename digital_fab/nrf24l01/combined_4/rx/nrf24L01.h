
/*
* ----------------------------------------------------------------------------
* “THE COFFEEWARE LICENSE” (Revision 1):
* <ihsan@kehribar.me> wrote this file. As long as you retain this notice you
* can do whatever you want with this stuff. If we meet some day, and you think
* this stuff is worth it, you can buy me a coffee in return.
* -----------------------------------------------------------------------------
*/


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


#define LOW 0
#define HIGH 1

#define nrf24_ADDR_LEN 5
#define nrf24_CONFIG ((1<<EN_CRC)|(0<<CRCO))

#define NRF24_TRANSMISSON_OK 0
#define NRF24_MESSAGE_LOST   1

//
// end of stuff from nrf24.h
//

void put_char(volatile unsigned char *port, unsigned char pin, char txchar);
void put_string(volatile unsigned char *port, unsigned char pin, char *str);


uint8_t spi_transfer(uint8_t tx);

/* send and receive multiple bytes over SPI */
void nrf24_transferSync(uint8_t* dataout,uint8_t* datain,uint8_t len);

/* send multiple bytes over SPI */
void nrf24_transmitSync(uint8_t* dataout,uint8_t len);

/* Clocks only one byte into the given nrf24 register */
void nrf24_configRegister(uint8_t reg, uint8_t value);

/* Read single register from nrf24 */
void nrf24_readRegister(uint8_t reg, uint8_t* value, uint8_t len);

/* Write to a single register of nrf24 */
void nrf24_writeRegister(uint8_t reg, uint8_t* value, uint8_t len);

void nrf24_powerUpRx();

void nrf24_powerUpTx();

void nrf24_powerDown();

void nrf24_init();

void nrf24_config(uint8_t channel, uint8_t pay_length);


/* Set the RX address */
void nrf24_rx_address(uint8_t * adr);


/* Returns the payload length */
uint8_t nrf24_payload_length();

/* Set the TX address */
void nrf24_tx_address(uint8_t* adr);

uint8_t nrf24_getStatus();


/* Checks if receive FIFO is empty or not */
uint8_t nrf24_rxFifoEmpty();


/* Checks if data is available for reading */
/* Returns 1 if data is ready ... */
uint8_t nrf24_dataReady();


/* Returns the length of data waiting in the RX fifo */
uint8_t nrf24_payloadLength();

/* Reads payload bytes into data array */
void nrf24_getData(uint8_t* data);

/* Returns the number of retransmissions occured for the last message */
uint8_t nrf24_retransmissionCount();

// Sends a data package to the default address. Be sure to send the correct
// amount of bytes as configured as payload on the receiver.
void nrf24_send(uint8_t* value);


uint8_t nrf24_isSending();



uint8_t nrf24_lastMessageStatus();
