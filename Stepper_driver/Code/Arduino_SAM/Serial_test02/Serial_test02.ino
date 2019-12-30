void setup() {
  SerialUSB.begin(0);
  pinMode(4, OUTPUT);
  //SerialUSB.flush();
}

void loop() {
  while(SerialUSB.available() < 2){;}
  digitalWrite(4, HIGH);
  if (SerialUSB.read() == 1 ) {       //if it's your address, flash LED according to second byte.
     int count = SerialUSB.read();
    for (int i=0; i<count; i++){
      digitalWrite(4, HIGH);
      delay(100);
      digitalWrite(4, LOW);
      delay(100);
    }
    //SerialUSB.flush();
  }
 
  else { digitalWrite(4, LOW);    //do nothing if not your address
    //SerialUSB.flush();
  }
  
}
