
#include <esp_now.h>
#include <WiFi.h>

// the number of the PWM pin
const int ledPin = 21;  

// setting PWM properties
const int freq = 5000;
const int ledChannel = 0;
const int resolution = 12;   //use 12 bits of resolution on both ADC and PWM.  Why not.

byte myData = 0;

 // callback function that will be executed when data is received
void OnDataRecv(const uint8_t * mac, const uint8_t *incomingData, int len) {
  memcpy(&myData, incomingData, sizeof(myData));
  Serial.print("Bytes received: ");
  Serial.println(len);
  Serial.print("byte: ");
  Serial.println(myData);
}



void setup(){
  Serial.begin(115200);

  // Set device as a Wi-Fi Station
  WiFi.mode(WIFI_STA);

  // Init ESP-NOW
  if (esp_now_init() != ESP_OK) {
    Serial.println("Error initializing ESP-NOW");
    return;
  }
  
  // Once ESPNow is successfully Init, we will register for recv CB to
  // get recv packer info
  esp_now_register_recv_cb(OnDataRecv);
  
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

  ledcWrite(ledChannel, 4095-dutyCycle);
  Serial.print(sensorValue);
  Serial.print(",  ");
  Serial.println(dutyCycle);
  delay(100);
  
}
