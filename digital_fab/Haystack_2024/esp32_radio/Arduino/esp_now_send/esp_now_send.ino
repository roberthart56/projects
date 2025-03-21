/*
  Rui Santos
  Complete project details at https://RandomNerdTutorials.com/esp-now-two-way-communication-esp32/

  Simplified for demo purposes by R Hart and N Melenbrink 3/29/22.

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files.

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.
  1/8/24
  1:  34:85:18:24:EB:74  {0x34,0x85,0x18,0x24,0xEB,0x74}
  2:  34:85:18:04:05:FC  {0x34,0x85,0x18,0x04,0x05,0xFC}
  3:  34:85:18:03:C0:BC  {0x34, 0x85, 0x18, 0x03, 0xC0, 0xBC}
*/

#include <esp_now.h>
#include <WiFi.h>


// REPLACE WITH THE MAC Address of your receiver.  Code is the same for both boards, with the exception of the following line.
uint8_t broadcastAddress[] =  {0x34,0x85,0x18,0x24,0xEB,0x74};    //this is board no 1.
//uint8_t broadcastAddress[] =  {0x34,0x85,0x18,0x04,0x05,0xFC};  //this is board no 2

// Variable to store if sending data was successful
String success;

//byte incomingByte;
byte outgoingByte;


// Callback when data is sent
void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
  Serial.print("\r\nLast Packet Send Status:\t");
  Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Delivery Success" : "Delivery Fail");
  if (status ==0){
    success = "Delivery Success :)";
  }
  else{
    success = "Delivery Fail :(";
  }
}

// // Callback when data is received
// void OnDataRecv(const uint8_t * mac, const uint8_t *incomingData, int len) {
//   memcpy(&incomingByte, incomingData, sizeof(incomingByte));
//   Serial.print("Bytes received: ");
//   Serial.println(len);
// }

void setup() {
  // Init Serial Monitor
  Serial.begin(115200);


  // Set device as a Wi-Fi Station
  WiFi.mode(WIFI_STA);

  // Init ESP-NOW
  if (esp_now_init() != ESP_OK) {
    Serial.println("Error initializing ESP-NOW");
    return;
  }

  // Register for a callback function that will be called when data is sent
  esp_now_register_send_cb(OnDataSent);

  // Register peer
  esp_now_peer_info_t peerInfo;
  memset(&peerInfo, 0, sizeof(peerInfo));
  memcpy(peerInfo.peer_addr, broadcastAddress, 6);
  peerInfo.channel = 0;  
  peerInfo.encrypt = false;

  // Add peer        
  if (esp_now_add_peer(&peerInfo) != ESP_OK){
    Serial.println("Failed to add peer");
    return;
  }
//   // Register for a callback function that will be called when data is received
//   esp_now_register_recv_cb(OnDataRecv);
}

void loop() {
  Serial.println(outgoingByte);
  outgoingByte = outgoingByte + 1;

  // Send message via ESP-NOW
  esp_err_t result = esp_now_send(broadcastAddress, (uint8_t *) &outgoingByte, sizeof(outgoingByte));

  if (result == ESP_OK) {
    Serial.println("Sent with success");
  }
  else {
    Serial.println("Error sending the data");
  }

 delay(100);

}