/* config.h
 * Author: Gianfranco Caputo       Created: 23/03/2016 12:01:57  */ 

#ifndef CONFIG_H_
#define CONFIG_H_

//-----------------------Pinout configuration

// Debug LED
#define LED_PORT					PORTB
#define LED_DDR						DDRB
#define LED_PIN						PINB
#define LED							(1 << PB2)

// NRF24L01 
#define RF24_PORT					PORTA
#define RF24_DDR					DDRA
#define RF24_PIN					PINA
#define RF24_MOSI					(1 << PA3)
#define RF24_MISO					(1 << PA7)
#define RF24_SCK					(1 << PA2)
#define RF24_CSN					(1 << PA1)
#define RF24_CE						(1 << PA0)

// Actuators
#define OUT_PORT					PORTB
#define OUT_DDR						DDRB
#define OUT_PIN						PINB
#define OUT1						(1 << PB0)
#define OUT2						(1 << PB1)

#endif /* CONFIG_H_ */