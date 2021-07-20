void setup() {
 //Serial.begin(9600);
 Serial.begin(31250);
 
}

void MidiSend(int one, int two, int three) {
  Serial.write(one);
  Serial.write(two);
  Serial.write(three);
  }

void loop() {
 delay(500);
 MidiSend(0X90, 0X38, 0X40);  //send note on to channel 1 at velocity 64
 delay(500);
 MidiSend(0X80, 0X38, 0X40);  //send note off to channel 1 at velocity 64
}
