const int Numpins=10;
int pin_array[Numpins]={2,3,4,5,6,7,8,9,10,11};
int note_array[Numpins] = {41,42,43,44,45,46,47,48,49,50};
bool switch_read[Numpins];
bool switch_previous[Numpins];

void setup() {
 Serial.begin(115200);
 Serial1.begin(31250);  //pins 18 and 19.
 for(int i=0; i<Numpins; i++) pinMode(pin_array[i], INPUT_PULLUP);
 for(int i=0; i<Numpins; i++) switch_previous[i] = 1;
 pinMode(13, OUTPUT);
}

void MidiSend(int one, int two, int three) {
  Serial1.write(one);
  Serial1.write(two);
  Serial1.write(three);
  }

void loop() {
for(int i=0; i<Numpins; i++) switch_read[i]=digitalRead(pin_array[i]);
//digitalWrite(13, switch_read[0]);  //Test pin2

for(int i=0; i<Numpins; i++){
  if( switch_read[i] != switch_previous[i]){
    if( (switch_previous[i]) & !(switch_read[i])){
       MidiSend(0X90, note_array[i], 0X40);  //send note on to channel 1 at velocity 64
       Serial.print("Turned on ");
       Serial.println(note_array[i]);
    }
    else {
      MidiSend(0X80, note_array[i], 0X40);  //send note off to channel 1 at velocity 64
      Serial.print("Turned off ");
       Serial.println(note_array[i]);
    }
    switch_previous[i] = switch_read[i];
  }
}
}
