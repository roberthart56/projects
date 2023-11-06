/*
  Blink
  Turns on an LED on for one second, then off for one second, repeatedly.

  Most Arduinos have an on-board LED you can control. On the Uno and
  Leonardo, it is attached to digital pin 13. If you're unsure what
  pin the on-board LED is connected to on your Arduino model, check
  the documentation at http://www.arduino.cc

  This example code is in the public domain.

  modified 8 May 2014
  by Scott Fitzgerald
 */

byte out1 = 2;
byte out2 = 3;

void setup() {
  
  pinMode(out1, OUTPUT);
  pinMode(out2, OUTPUT);
}

// the loop function runs over and over again forever
void loop() {
  digitalWrite(out1, HIGH);   // turn the LED on (HIGH is the voltage level)
  digitalWrite(out2, HIGH);
  delay(200);              // wait for a second
  digitalWrite(out1, LOW);    // turn the LED off by making the voltage LOW
  digitalWrite(out2, LOW); 
  delay(600);              // wait for a second
}
