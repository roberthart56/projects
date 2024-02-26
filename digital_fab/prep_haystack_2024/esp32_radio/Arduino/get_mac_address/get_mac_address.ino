/* 1/8/24
  1:  34:85:18:24:EB:74  {0x34,0x85,0x18,0x24,0xEB,0x74}
  2:  34:85:18:04:05:FC  {0x34,0x85,0x18,0x04,0x05,0xFC}
  3:  34:85:18:03:C0:BC  {0x34, 0x85, 0x18, 0x03, 0xC0, 0xBC}
*/
#include "WiFi.h"

void setup(){
  Serial.begin(115200);
  WiFi.mode(WIFI_MODE_STA);
  Serial.println(WiFi.macAddress());
}

void loop(){
  Serial.println(WiFi.macAddress());
  delay(500);

}