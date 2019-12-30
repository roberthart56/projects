
int Aplus = A0;
int Aminus = A1;
int Bplus = A2;
int Bminus = A3;

int step_pin = 7;
int dir_pin = 9;
int step_count = 0;

void setup() {

  pinMode(Aplus, OUTPUT);
  pinMode(Aminus, OUTPUT);
  pinMode(Bplus, OUTPUT);
  pinMode(Bminus, OUTPUT);
}

void pulse_0(){
  digitalWrite(Aplus,HIGH);
  digitalWrite(Bplus,HIGH);
  
}

void pulse_1(){
  digitalWrite(Aplus,HIGH);
  digitalWrite(Bminus,HIGH);
}

void pulse_2(){
  digitalWrite(Aminus,HIGH);
  digitalWrite(Bplus,HIGH);
}

void pulse_3(){
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
  if (step_count == 0) pulse_0();
  if (step_count == 1) pulse_1();
  if (step_count == 2) pulse_2();
  if (step_count == 3) pulse_3();

  delay(1000);
  all_off();
  delay(1000);
  step_count ++;
  step_count = step_count%4;
 }
