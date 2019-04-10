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
const byte out[] = {2,3,4,5,6,7,8,9,10};



void setup() {
  Serial.begin(115200); 
  
  for(int i = 0; i < sizeof(out); i++){
    pinMode(out[i], OUTPUT);
  }  
}

void motor_on(byte N){
  digitalWrite(N,HIGH);
}

void motor_off(byte N){
  digitalWrite(N,LOW);
}

void loop() {
  byte n= random(0,3);
  motor_on(n);
  delay(200);
  motor_off(n);
  delay(600);
  Serial.println(n);
}
