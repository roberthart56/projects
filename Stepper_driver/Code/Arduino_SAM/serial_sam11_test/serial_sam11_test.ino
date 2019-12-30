void setup() {
  Serial.begin(0);
}

void loop() {
  while(Serial.available() < 3){
    ;}
  int count  = Serial.available();
  Serial.println (Serial.available());
  for (int i =0; i< count; i++){
  Serial.println ((char)Serial.read());
  }
  
  delay(500);
}
