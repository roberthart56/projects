/*
Stepper program.  Input pins for direction and step.  Steps when step-pin goes high.
 
*/
int Aplus = 15;
int Aminus = 14;
int Bplus = 8;
int Bminus = 5;

int step_pin = 2;
int dir_pin = 4;
uint16_t step_count = 0;

void setup() {
  SerialUSB.begin(0);
  pinMode(Aplus, OUTPUT);
  pinMode(Aminus, OUTPUT);
  pinMode(Bplus, OUTPUT);
  pinMode(Bminus, OUTPUT);
  pinMode(step_pin, INPUT_PULLDOWN);
  pinMode(dir_pin, INPUT_PULLDOWN);
}

void pulse_0(){
  digitalWrite(Aplus,HIGH);
  digitalWrite(Bplus,HIGH);
}

void pulse_1(){
  digitalWrite(Aminus,HIGH);
  digitalWrite(Bplus,HIGH);
}

void pulse_2(){
  digitalWrite(Aminus,HIGH);
  digitalWrite(Bminus,HIGH);
}

void pulse_3(){
  digitalWrite(Aplus,HIGH);
  digitalWrite(Bminus,HIGH);
}

void all_off() {
  digitalWrite(Aplus,LOW);
  digitalWrite(Aminus,LOW);
  digitalWrite(Bplus,LOW);
  digitalWrite(Bminus,LOW);
}

void loop() {
  
  while(!digitalRead(step_pin)){      //wait for step pin to go high.
    ;} 
  
  all_off();                          //turn off coils before sending new step.

  if (digitalRead(dir_pin))  step_count --;   //check direction.
  else step_count ++;
  
  
  step_count = step_count%4;
  SerialUSB.println(step_count); 
  
  if (step_count == 0) pulse_0();
  if (step_count == 1) pulse_1();
  if (step_count == 2) pulse_2();
  if (step_count == 3) pulse_3();  
  delay(2);
  
 }
