// the number of the PWM pin
const int ledPin = 21;  

// setting PWM properties
const int freq = 5000;
const int ledChannel = 0;
const int resolution = 12;   //use 12 bits of resolution on both ADC and PWM.  Why not.
 
void setup(){
  Serial.begin(115200);
  
  // configure PWM functionalitites
  ledcSetup(ledChannel, freq, resolution);
  
  // attach the channel to the GPIO to be controlled
  ledcAttachPin(ledPin, ledChannel);
}
 
void loop(){
  int dutyCycle=0; 
  int setpoint = 2000;
  int sensorValue = analogRead(A0);
  int delta_v = sensorValue-setpoint;
 
  if (delta_v < 0) dutyCycle = 0;
  else dutyCycle = delta_v *10;
  if (dutyCycle > 4095) dutyCycle = 4095;

  ledcWrite(ledChannel, dutyCycle);
  Serial.print(sensorValue);
  Serial.print(",  ");
  Serial.println(dutyCycle);
  delay(15);
  
}
