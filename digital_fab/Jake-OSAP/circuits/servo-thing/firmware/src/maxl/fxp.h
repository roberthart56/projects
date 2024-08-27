#ifndef FXP_H_
#define FXP_H_

#include <Arduino.h>

typedef int32_t fxp32_16_t;

fxp32_16_t fxp32_16_mult(fxp32_16_t a, fxp32_16_t b);

fxp32_16_t fxp32_16_fromFloat(float a);
float fxp32_16_toFloat(fxp32_16_t a);

fxp32_16_t fxp32_16_fromUInt32(uint32_t a);
fxp32_16_t fxp32_16_fromInt32(int32_t a);

#endif 