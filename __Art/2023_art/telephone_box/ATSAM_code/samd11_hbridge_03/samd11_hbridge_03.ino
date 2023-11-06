/*
H-bridge driver for telephone box project.  responds to potentiometer. 
*/
int Aplus = 15;
int Aminus = 14;

int LED_G = 4;    //LEDs are attached to pins to give a visual indication of direction and step
int LED_R = 2;
uint8_t rec_byte = 0;         //The byte received from USART

int motor_speed = 0;

void setup() {
  SerialUSB.begin(0);
  Serial1.begin(115200);
  pinMode(Aplus, OUTPUT);
  pinMode(Aminus, OUTPUT);
  pinMode(LED_G, OUTPUT);
  pinMode(LED_R, OUTPUT);
 }


void all_off() {
  digitalWrite(Aplus,LOW);
  digitalWrite(Aminus,LOW);
 
}

void loop() {
//  while (!Serial1.available()){       //wait until serial is available.
//  }
//
if (Serial1.available() ){
rec_byte =  Serial1.read(); 
}

int setpoint = rec_byte;
int pot_voltage = analogRead(5);
int delta_v = pot_voltage/4 - setpoint;

if (delta_v < 0) motor_speed = 0;
else motor_speed = delta_v *10;
if(motor_speed > 100) motor_speed = 100;      //my h-bridge stops working at hig duty cycle.

analogWrite(Aminus,motor_speed );
SerialUSB.print(setpoint);
SerialUSB.print(",  ");
SerialUSB.print(pot_voltage/4); 
SerialUSB.print(",  ");
SerialUSB.println(motor_speed);
delay(10);
 }
