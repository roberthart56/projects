#ifndef FP_CLOCK_UTILS_H_
#define FP_CLOCK_UTILS_H_

#include <Arduino.h>

typedef int64_t fpint64_t;

int64_t fp_fixed64ToInt64(fpint64_t fixed);
float fp_fixed64ToFloat32(fpint64_t fixed);

fpint64_t fp_int64ToFixed64(int64_t integer);
fpint64_t fp_float32ToFixed64(float flt);

fpint64_t fp_mult64x64_bigLittle(fpint64_t big, fpint64_t little);

#endif 