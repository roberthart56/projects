#include "osap/src/osap.h"
#include "maxl/maxl.h"
#include <Servo.h>

#define PIN_ABTRANS D8
#define PIN_YZTRANS D10
#define PIN_LED_WD PIN_LED_G 

#define PIN_SERVO 29 

Servo servo; 

void writeMicroseconds(uint16_t us){
  servo.writeMicroseconds(us);
}

OSAP_Runtime osap("ServoThing", "servo_z");
OSAP_Gateway_USBCDC_COBS<decltype(Serial)> serLink(&Serial, "usb");
// OSAP_Gateway_UART_COBS_CRC16<decltype(Serial1)> mudLink(&Serial1, 1000000, 
//   "backpack_mudl",
//   PIN_YZTRANS, PIN_ABTRANS
// );

BUILD_RPC(writeMicroseconds, "us", "");

MAXL maxl;

// maxl's api... or should we just make it a port ? 
void maxl_setInterval(uint8_t interval){
  maxl.setInterval(interval);
}

void maxl_addControlPoint(uint64_t timestamp, float pt, uint8_t flags){
  maxlFlags_t _flags = { .byte = flags };
  maxl.addControlPoint(timestamp, fxp32_16_fromFloat(pt), _flags);
}

auto maxl_getPosition(void){
  return std::make_tuple(osap.getSystemMicroseconds(), maxl.getPosition());
}

String maxl_getErrorMessage(void){
  return maxl.getErrorMessage();
}

BUILD_RPC(maxl_setInterval, "intervalNumBits", "");
BUILD_RPC(maxl_addControlPoint, "time, point, flags", "");
BUILD_RPC(maxl_getErrorMessage, "", "");

BUILD_RPC(maxl_getPosition, "", "time, position");


#define ALARM_DT_NUM 1
#define ALARM_DT_IRQ TIMER_IRQ_1

// 1khz aught to be enough for these 
const uint32_t _delT_us = 10000;

// let's get our tight loop, 
void alarm_handler(void){
  // the ISR 
  hw_clear_bits(&timer_hw->intr, 1u << ALARM_DT_NUM);
  timer_hw->alarm[ALARM_DT_NUM] = (uint32_t) (timer_hw->timerawl + _delT_us);

  // get the target posn, 
  maxl_eval_t eval = maxl.evaluate(osap.getSystemMicroseconds());

  // posn is basically current value 
  if(eval.isValid){
    float posAsFloat = fxp32_16_toFloat(eval.pos);
    // let's make sure this is an int 
    if(posAsFloat < 500.0F) posAsFloat = 500.0F;
    if(posAsFloat > 2500.0F) posAsFloat = 2500.0F;
    uint16_t microseconds = int(posAsFloat);
    writeMicroseconds(microseconds);
  }
}

void alarm_begin(void){
  // setup the hardware timer 
  hw_set_bits(&timer_hw->inte, 1u << ALARM_DT_NUM);
  irq_set_exclusive_handler(ALARM_DT_IRQ, alarm_handler);
  irq_set_enabled(ALARM_DT_IRQ, true);
  timer_hw->alarm[ALARM_DT_NUM] = (uint32_t) (timer_hw->timerawl + _delT_us);
}


void setup() {
  osap.begin();
  maxl.begin();
  alarm_begin();

  servo.attach(PIN_SERVO, 500, 2500);
  pinMode(PIN_LED_WD, OUTPUT);
}


uint32_t wdBlinkInterval = 50;
uint32_t wdBlinkLast = 0; 
uint16_t usToWrite = 500;

void loop() {
  osap.loop(); 

  // writeMicroseconds(usToWrite);
  // usToWrite += 20;
  // if(usToWrite > 2500) usToWrite = 500;
  // delay(100);

  if(wdBlinkLast + wdBlinkInterval < millis()){
    wdBlinkLast = millis();
    digitalWrite(PIN_LED_WD, !digitalRead(PIN_LED_WD));
  }
}

