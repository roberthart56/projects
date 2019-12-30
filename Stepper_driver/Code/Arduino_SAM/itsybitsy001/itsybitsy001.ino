
int Aplus = A0;
int Aminus = A1;
int Bplus = A2;
int Bminus = A3;


void setup() {

  pinMode(Aplus, OUTPUT);
  pinMode(Aminus, OUTPUT);
  pinMode(Bplus, OUTPUT);
  pinMode(Bminus, OUTPUT);
}

void pulse_1(){
  digitalWrite(Aplus,HIGH);
  digitalWrite(Bplus,HIGH);
  
}

void pulse_2(){
  digitalWrite(Aplus,HIGH);
  digitalWrite(Bminus,HIGH);
}

void pulse_3(){
  digitalWrite(Aminus,HIGH);
  digitalWrite(Bplus,HIGH);
}

void pulse_4(){
  digitalWrite(Aminus,HIGH);
  digitalWrite(Bminus,HIGH);
}

void all_off() {
  digitalWrite(Aplus,LOW);
  digitalWrite(Aminus,LOW);
  digitalWrite(Bplus,LOW);
  digitalWrite(Bminus,LOW);
}

void loop() {
  pulse_1();
  delay(100);
  all_off();
  delay(100);
  pulse_2();
  delay(100);
  all_off();
  delay(100);
  pulse_3();
  delay(100);
  all_off();
  delay(100);
  pulse_4();
  delay(100);
  all_off();
  delay(100);
 }
