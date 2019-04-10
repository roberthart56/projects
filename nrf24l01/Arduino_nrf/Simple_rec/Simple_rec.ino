
/*
* Simple sketch for nRF24L01+ radios  Receive side.
* 
* Updated: Dec 2014 by TMRh20. Simplified Mar 2019 RMH.
*/

#include <SPI.h>
#include "RF24.h"
#include <Servo.h>

Servo myservo; 
int val = 0;
/* Hardware configuration: Set up nRF24L01 radio on SPI bus plus pins 7 & 8 */
RF24 radio(7,8);


byte addresses[][6] = {"1Node","2Node"};
int angle;

void setup() {
  
  Serial.begin(115200);
  Serial.println(F("RF24example:  simple receive"));
  myservo.attach(2);
  
  radio.begin();

  // Set the PA Level low to prevent power supply related issues since this is a
 // getting_started sketch, and the likelihood of close proximity of the devices. RF24_PA_MAX is default.
  radio.setPALevel(RF24_PA_LOW);
  
 
    radio.openWritingPipe(addresses[1]);
    radio.openReadingPipe(1,addresses[0]);
 
  
  // Start the radio listening for data
  radio.startListening();
}

void loop() {

    byte rec_data;
    
    if( radio.available()){
                                                                    // Variable for the received timestamp
      while (radio.available()) {                                   // While there is data ready
        radio.read( &rec_data, 1 );             // Get the payload
      }
     val = map(rec_data, 0, 255, 0, 180);  
      myservo.write(val);
      Serial.print("received ");
      Serial.println(rec_data); 
      
      
   }



} // Loop

