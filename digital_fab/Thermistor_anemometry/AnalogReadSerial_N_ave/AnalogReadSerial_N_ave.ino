/*
  AnalogReadSerial
  Reads an analog input on pin 0, prints the result to the serial monitor.
  Graphical representation is available using serial plotter (Tools > Serial Plotter menu)
  Attach the center pin of a potentiometer to pin A0, and the outside pins to +5V and ground.

  This example code is in the public domain.
*/
int N=1000; //number to average

void setup() {
  // initialize serial communication at 9600 bits per second:
  Serial.begin(9600);
  //analogReference(INTERNAL);
}

float sensorAve = 0;


void loop() {
  // read the input on analog pin 0:
 long int sum = 0;

  for (int i=1; i<N+1; i++){
  int sensorValue = analogRead(A0);
  sum = sum + sensorValue;
  }

  sensorAve = (float)sum/(float)N;    //necessary to cast 
                                      //integer variables as float, 
                                      //in order to get result to be
                                      //floating point number.
  
  //Serial.println(sum);
  Serial.println(sensorAve);
  
}
