/*
Stepper program.  USB serial sends number of steps.  Steps at a constant rate.
*/
int Aplus = 15;
int Aminus = 14;
int Bplus = 8;
int Bminus = 5;

int step_num = 1;
uint16_t step_count = 0;
uint8_t pulse_count = 0;

void setup() {
  SerialUSB.begin(0);
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
  
  while (!SerialUSB.available()){
  }
  
  step_num =  SerialUSB.read();

  for(int i=0; i<step_num; i++){                  
    step_count ++;    //NEXT, do a conditional dependent on direction bit and -- or ++.
    pulse_count = step_count%4;
    
    SerialUSB.println(step_count);    //keep track of overall step_count,  16 bit unsigned integer.
    
    all_off();
    delayMicroseconds(10);
    
    if (pulse_count == 0) pulse_0();
    if (pulse_count == 1) pulse_1();
    if (pulse_count == 2) pulse_2();
    if (pulse_count == 3) pulse_3(); 

    delay(10);      //milliseconds  
    }
 }
