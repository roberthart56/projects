/*
  N_blink
  to use with nine motors
 */
const byte out[] = {2,3,4,5,6,7,8,9,10};
const int total_delay[] = {1200,1800,1600,6000,100,4000,1500,300,300};


void setup() {
  Serial.begin(115200); 
  
  for(int i = 0; i < sizeof(out); i++){     //set up all pins for output
    pinMode(out[i], OUTPUT);
  }  
}

void motor_on(byte N){                //function to turn on motor
  digitalWrite(N,HIGH);
}

void motor_off(byte N){                 //function to turn off motor
  digitalWrite(N,LOW);
}

void loop() {
  
  for(int i=0; i < 9;  i++){
    byte n= random(0,3);
    motor_on(out[n]);             //turn nth motor on
    delay(200);
    motor_off(out[n]);              //turn nth moto off
    delay(total_delay[i]);
    //Serial.println(n);
  }
}
