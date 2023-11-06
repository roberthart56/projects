
/*
   This examples shows how to make a simple seven keys MIDI keyboard with volume control
   Created: 4/10/2015
   Author: Arturo Guadalupi <a.guadalupi@arduino.cc>
   http://www.arduino.cc/en/Tutorial/MidiDevice
*/

#include "MIDIUSB.h"



void setup() {
  Serial1.begin(31250);
  Serial.begin(0);
}

void loop() {
  Serial1.flush();
  while (Serial1.available()< 3){       //wait until serial has three bytes.
  }
  
  byte rec_byte1 =  Serial1.read();
  byte rec_byte2 =  Serial1.read();
  byte rec_byte3 =  Serial1.read();
  
   byte par1 = (rec_byte1 & 0xF0)>>4;  //Strip chennle information and move to least sig nybble.
   Serial.print(par1, HEX);
   byte par2= rec_byte1;
   byte par3 = rec_byte2;
   byte par4 = rec_byte3;
   
   
   midiEventPacket_t note = {par1, par2, par3, par4};
   MidiUSB.sendMIDI(note);
   MidiUSB.flush();
}

// First parameter is the event type (0x09 = note on, 0x08 = note off).
// Second parameter is note-on/note-off, combined with the channel.
// Channel can be anything between 0-15. Typically reported to the user as 1-16.
// Third parameter is the note number (48 = middle C).
// Fourth parameter is the velocity (64 = normal, 127 = fastest).
