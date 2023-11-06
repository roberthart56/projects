/*
  N_blink
  to use with nine motors
 */
const byte out[] = {2,3,4,5,6,7,8,9,10};
int off_delay;
int a,b,c;

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
  
    off_delay = random(0,100);
    byte n1= random(0,9);   //not inclusive of high value
    byte n2= random(0,9);   //not inclusive of high value
    
    delay(off_delay);
    Serial.print(n1);
    Serial.print(", ");
    Serial.println(off_delay);
    
    motor_on(out[n1]);             //turn nth motor on
    motor_on(out[n2]);             //turn nth motor on
    delay(200);
    motor_off(out[n1]);              //turn nth motor off
     motor_off(out[n2]);
  
}
