/*
  Blink
  
 */
int d1;
int d2;
int d3;


void setup() {
  
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);
}

// the loop function runs over and over again forever
void loop() {
  d1 = random(0,200);
  d2 = random(0,500);
  d3 = random(0,500);
  digitalWrite(3, HIGH);  
  delay(d1);
  digitalWrite(4, HIGH);
  delay(d2);
  digitalWrite(5, HIGH);
  //delay(50);
  digitalWrite(3, LOW);   
  delay(d3);
  digitalWrite(4, LOW);   
  delay(d1);
  digitalWrite(5, LOW); 
               
}
