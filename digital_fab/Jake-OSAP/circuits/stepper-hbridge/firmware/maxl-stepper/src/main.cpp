#include <Adafruit_NeoPixel.h>
#include "osap/src/osap.h"
#include "motion/stepperDriver.h"
#include "maxl/maxl.h"

#define PIN_NEOPIXEL 12 
#define PIN_NEOPIXEL_POWER 11 

Adafruit_NeoPixel pixel(1, PIN_NEOPIXEL, NEO_GRB + NEO_KHZ800);

#define PIN_ABTRANS D8
#define PIN_YZTRANS D10
#define PIN_LED_WD PIN_LED_G 
#define PIN_LIMIT D0 

// motor_x_back
// motor_x_front
// motor_y 

OSAP_Runtime osap("MAXLStepper", "motor_elbow");
OSAP_Gateway_USBCDC_COBS<decltype(Serial)> serLink(&Serial, "usb");
// OSAP_Gateway_UART_COBS_CRC16<decltype(Serial1)> mudLink(&Serial1, 1000000, 
//   "backpack_mudl",
//   PIN_YZTRANS, PIN_ABTRANS
// );


// HI when limit is hit 
std::tuple<uint64_t, bool> getLimitState(void){
  return std::make_tuple(osap.getSystemMicroseconds(), digitalRead(PIN_LIMIT));
}

// 0-1.0F ! 
void setCurrentScale(float duty){
  if(duty > 1.0F) duty = 1.0F;
  if(duty < 0.0F) duty = 0.0F;
  stepper_setAmplitude(1024 * duty);
}

void setFinalScalar(float scalar);


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

BUILD_RPC(setCurrentScale, "duty", ""); 
BUILD_RPC(getLimitState, "", "time, state");
BUILD_RPC(setFinalScalar, "scalar", "");

BUILD_RPC(maxl_setInterval, "intervalNumBits", "");
BUILD_RPC(maxl_addControlPoint, "time, point, flags", "");
BUILD_RPC(maxl_getErrorMessage, "", "");

BUILD_RPC(maxl_getPosition, "", "time, position");


#define ALARM_DT_NUM 1
#define ALARM_DT_IRQ TIMER_IRQ_1

// 8khz for now... pre-computing a...d might let us get to 10's of khz 
const uint32_t _delT_us = 125;

// warning also that this scaling, while having the nice convenience of 
// one integer per revolution, does use less precision than we have access to w/ this driver 
fxp32_16_t final_motor_scalar = fxp32_16_fromFloat(1.5625F);

void setFinalScalar(float scalar){
  final_motor_scalar = fxp32_16_fromFloat(scalar);
}

// let's get our tight loop, 
void alarm_handler(void){
  // clear handly 
  hw_clear_bits(&timer_hw->intr, 1u << ALARM_DT_NUM);
  timer_hw->alarm[ALARM_DT_NUM] = (uint32_t) (timer_hw->timerawl + _delT_us);

  // digitalWrite(PIN_LIMIT, HIGH);
  maxl_eval_t eval = maxl.evaluate(osap.getSystemMicroseconds());
  // digitalWrite(PIN_LIMIT, LOW);
  // uuuuhhh: 0-2PI phase ang is 0-2048, 
  // 0-2PI phase ang is 4 steps... one full rev is 50 * 2048: 102400
  // direct convert works out so that lower 16 (decimal of position) 
  // is ~ 1/2 of a full turn (but not exactly: 65k / 102k)
  // actually to convert to maxl-integer-place to revs is exactly 1.5625, 
  // so to make our motor such that `1.0` in MAXL is one revolution... 
  if(eval.isValid){
    // although *warning* that this will also overflow that much faster... 
    stepper_point(fxp32_16_mult(eval.pos, final_motor_scalar));
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
  pixel.begin();
  osap.begin();
  maxl.begin();
  stepper_init();
  alarm_begin();
  pinMode(PIN_LIMIT, INPUT_PULLUP);
  // pinMode(PIN_LIMIT, OUTPUT);
  pinMode(PIN_LED_WD, OUTPUT);
  pinMode(PIN_NEOPIXEL_POWER, OUTPUT);
  digitalWrite(PIN_NEOPIXEL_POWER, HIGH);
}


uint32_t wdBlinkInterval = 50;
uint32_t wdBlinkLast = 0; 
bool blinkState = false;

void loop() {
  osap.loop(); 

  if(wdBlinkLast + wdBlinkInterval < millis()){
    wdBlinkLast = millis();
    digitalWrite(PIN_LED_WD, !digitalRead(PIN_LED_WD));
    if(blinkState){
      pixel.setPixelColor(0, pixel.Color(0, 100, 0));
    } else {
      pixel.setPixelColor(0, pixel.Color(0, 0, 0));
    }
    pixel.show();
    blinkState = !blinkState; 
  }
}

