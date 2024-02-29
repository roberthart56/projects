/*
  Blink
*/
const int outpin = D5;

void setup() {
  // initialize digital pin oupin as an output.
  pinMode(outpin, OUTPUT);
}

// the loop function runs over and over again forever
void loop() {
  digitalWrite(outpin, HIGH);  // turn the LED on (HIGH is the voltage level)
  delay(1000);                      // wait for a second
  digitalWrite(outpin, LOW);   // turn the LED off by making the voltage LOW
  delay(1000);                      // wait for a second
}
