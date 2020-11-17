//
// hello.t412.echo.ino
//
// tiny412 echo hello-world
//    115200 baud
//
// Neil Gershenfeld 12/8/19
//
// This work may be reproduced, modified, distributed,
// performed, and displayed for any purpose, but must
// acknowledge this project. Copyright is retained and
// must be preserved. The work is provided as is; no
// warranty is provided, and users accept all liability.
//

#define max_buffer 25

static int index = 0;
static char chr;
static char buffer[max_buffer] = {0};

void setup() {
   Serial.swap(1);
   Serial.begin(115200);
   }

void loop() {
   if (Serial.available() > 0) {
      chr = Serial.read();
      Serial.print("hello.t412.echo: you typed \"");
      buffer[index++] = chr;
      if (index == (max_buffer-1))
         index = 0;
      Serial.print(buffer);
      Serial.println("\"");
      }
   }
