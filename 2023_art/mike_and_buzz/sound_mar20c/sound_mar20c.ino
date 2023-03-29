//sound_mar20c.  Robert Hart March 20, 2019.
// program to use with sound input to generate feedback.
// microphone on A0
// Piezo buzzer on digital pin 2.
// Has some random clicks to start the feedback.  


void setup() {
  //Serial.begin(115200);     // initialize serial communication at 115200 bits per second:
  pinMode(2, OUTPUT);
}

        


void loop() {          
  digitalWrite(2,HIGH);     //make a chirp
  digitalWrite(2,LOW);
  int N = random(1,50);     //Random number of times through the loop.  This makes chirp appear at random times.
  for (int i = 0; i<N; i++){
    int sound1= analogRead(A0);
    int sound2= analogRead(A0);
    if (sound1-sound2 > 1) digitalWrite(2, HIGH);     //output to pin2 depends on difference
    if (sound1-sound2 < -1) digitalWrite(2,LOW);      //between two close readings
    }
}

