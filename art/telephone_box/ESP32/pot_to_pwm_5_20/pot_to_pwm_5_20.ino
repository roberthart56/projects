// the number of the LED pin
const int ledPin = 21;  // 16 corresponds to GPIO16

// setting PWM properties
const int freq = 5000;
const int ledChannel = 0;
const int resolution = 8;
 
void setup(){
  Serial.begin(115200);
  
  // configure LED PWM functionalitites
  ledcSetup(ledChannel, freq, resolution);
  
  // attach the channel to the GPIO to be controlled
  ledcAttachPin(ledPin, ledChannel);
}
 
void loop(){
 int sensorValue = analogRead(A0);
 int dutyCycle = sensorValue/8;
 ledcWrite(ledChannel, dutyCycle);
 delay(15);
  
}
