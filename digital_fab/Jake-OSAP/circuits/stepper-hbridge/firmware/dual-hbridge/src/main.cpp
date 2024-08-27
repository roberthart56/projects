#include "osap/src/osap.h"
#include "motion/stepperDriver.h"
#include "maxl/maxl.h"

#define PIN_ABTRANS D8
#define PIN_YZTRANS D10
#define PIN_LED_WD PIN_LED_G 
#define PIN_LIMIT D0 

#define AIN1_PIN 6      // on D4
#define AIN2_PIN 7      // on D5 
#define BIN1_PIN 28     // on D2
#define BIN2_PIN 4      // on D9 
#define APWM_PIN 27     // on D1
#define BPWM_PIN 29     // on D3 

void setupHBridges(void){
  pinMode(AIN1_PIN, OUTPUT);
  pinMode(AIN2_PIN, OUTPUT);
  pinMode(BIN1_PIN, OUTPUT);
  pinMode(BIN2_PIN, OUTPUT);
  pinMode(APWM_PIN, OUTPUT);
  pinMode(BPWM_PIN, OUTPUT);
}

void writeHBridgeOutputs(float coil_a, float coil_b){
  if(coil_a == 0.0F){
    digitalWrite(AIN1_PIN, LOW);
    digitalWrite(AIN2_PIN, LOW);
  } else if (coil_a > 0.0F){
    digitalWrite(AIN1_PIN, HIGH);
    digitalWrite(AIN2_PIN, LOW);
  } else {
    digitalWrite(AIN1_PIN, LOW);
    digitalWrite(AIN2_PIN, HIGH);
  }
  analogWrite(APWM_PIN, int(255 * abs(coil_a)));

  if(coil_b == 0.0F){
    digitalWrite(BIN1_PIN, LOW);
    digitalWrite(BIN2_PIN, LOW);
  } else if (coil_b > 0.0F){
    digitalWrite(BIN1_PIN, HIGH);
    digitalWrite(BIN2_PIN, LOW);
  } else {
    digitalWrite(BIN1_PIN, LOW);
    digitalWrite(BIN2_PIN, HIGH);
  }
  analogWrite(BPWM_PIN, int(255 * abs(coil_b)));
}


OSAP_Runtime osap("DualHBridge", "dual_thwapper");
OSAP_Gateway_USBCDC_COBS<decltype(Serial)> serLink(&Serial, "usb");
// OSAP_Gateway_UART_COBS_CRC16<decltype(Serial1)> mudLink(&Serial1, 1000000, 
//   "backpack_mudl",
//   PIN_YZTRANS, PIN_ABTRANS
// );

BUILD_RPC(writeHBridgeOutputs, "coil_a, coil_b", "");

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
const uint32_t _delT_us = 1000;

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
    writeHBridgeOutputs(posAsFloat, posAsFloat);
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
  stepper_init();
  alarm_begin();
  pinMode(PIN_LIMIT, INPUT_PULLUP);
  // pinMode(PIN_LIMIT, OUTPUT);
  pinMode(PIN_LED_WD, OUTPUT);
}


uint32_t wdBlinkInterval = 50;
uint32_t wdBlinkLast = 0; 

void loop() {
  osap.loop(); 

  if(wdBlinkLast + wdBlinkInterval < millis()){
    wdBlinkLast = millis();
    digitalWrite(PIN_LED_WD, !digitalRead(PIN_LED_WD));
  }
}

