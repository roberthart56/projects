/*
/works with signle byte.  Next add second byte.
/
/
*/

void setup() {
  SerialUSB.begin(0);
  pinMode(4, OUTPUT);
  //SerialUSB.flush();
}

void loop() {
while(!SerialUSB.available() ){;}
  SerialUSB.println(SerialUSB.available());
  if (SerialUSB.read() == 1 ) {       //if it's your address, flash LED according to second byte.
      digitalWrite(4, HIGH);
       
    }
    //SerialUSB.flush();
  else { digitalWrite(4, LOW);    //do nothing if not your address
    //SerialUSB.flush();
  }
  
}
