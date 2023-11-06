/*
Stepper program.  Input pins for direction and step.  Steps when step-pin goes high.
 
*/
int Aplus = 15;
int Aminus = 14;
int Bplus = 8;
int Bminus = 5;

int LED_G = 4;    //LEDs are attached to pins to give a visual indication of direction and step
int LED_R = 2;
uint8_t rec_byte = 0;         //The byte received from USART


void setup() {
  SerialUSB.begin(0);
  Serial1.begin(115200);
  pinMode(Aplus, OUTPUT);
  pinMode(Aminus, OUTPUT);
  pinMode(Bplus, OUTPUT);
  pinMode(Bminus, OUTPUT);
  pinMode(LED_G, OUTPUT);
  pinMode(LED_R, OUTPUT);
 }


void all_off() {
  digitalWrite(Aplus,LOW);
  digitalWrite(Aminus,LOW);
  digitalWrite(Bplus,LOW);
  digitalWrite(Bminus,LOW);
}

void loop() {
  while (!Serial1.available()){       //wait until serial is available.
  }

  //rec_byte =  Serial1.read();
  int pot_voltage = analogRead(8);
  analogWrite(Aplus, pot_voltage);
  Serial.println(pot_voltage); 
 }
