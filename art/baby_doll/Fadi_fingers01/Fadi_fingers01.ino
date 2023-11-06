const byte out[] = {2,4,5,8,9};


void setup() {
  Serial.begin(115200); 
  
  for(int i = 0; i < 5; i++){     //set up all pins for output
    pinMode(out[i], OUTPUT);
  }  
}
void loop() {
  for(int i = 0; i < 5; i++){     //set up all pins for output
    int n = random(0,5);
    int n2 = random(0,5);
    digitalWrite(out[n], HIGH);
    digitalWrite(out[n2], HIGH);
    
    delay(200);
    digitalWrite(out[n], LOW);
    digitalWrite(out[n2], LOW);
    
    delay(400+100*n);
    
  }  
}
