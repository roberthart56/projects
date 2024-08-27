#include "fp_clock_utils.h"

// I've picked 20 bits of precision, that means we can express down to 
// 1ppm of skew - 1us per second... seems like enough to start, 
// esp. since we can't measure any more than 1us offset anyways ! 

// 20 bits decimal:          1 048 576
// 44 bits integer: 17 592 186 044 416

const int32_t fp_scale = 22;

// this app typically multiplies one big by one little,
// i.e. an offset by a filtering value, or an interval by the skew.
// since after multiplication of 2^20 x 2^20 (1x1) we have only 2^22 bits, 
// we guard such that big, little do not combine to overflow this during 
// the intermediate step 
const int64_t fp_int_big_max = (1 << (64 - 2 * fp_scale)) - 1;
const int64_t fp_int_little_max = 2;

// const int32_t   fp_int_max =    32767;
// const int32_t   fp_int_min =   -32767;
// const int64_t   fp_32b_max =    2147483647;
// const int64_t   fp_32b_min =   -2147483647;

int64_t fp_fixed64ToInt64(fpint64_t fixed){
  return (fixed >> fp_scale);
}

float fp_fixed64ToFloat32(fpint64_t fixed){
  return ((float)fixed / (float)(1 << fp_scale));
}

fpint64_t fp_int64ToFixed64(int64_t integer){
  if(integer > fp_int_big_max) integer = fp_int_big_max;
  if(integer < - fp_int_big_max) integer = - fp_int_big_max;
  return (integer << fp_scale);
}

fpint64_t fp_float32ToFixed64(float flt){
  if(flt > (float)fp_int_big_max) return fp_int64ToFixed64(fp_int_big_max);
  if(flt < (float)(-fp_int_big_max)) return fp_int64ToFixed64(-fp_int_big_max);
  return (flt * (float)(1 << fp_scale));
}

fpint64_t fp_mult64x64_bigLittle(fpint64_t big, fpint64_t little){
  if(little > fp_int64ToFixed64(fp_int_little_max)) little = fp_int64ToFixed64(fp_int_little_max);
  if(little < fp_int64ToFixed64(-fp_int_little_max)) little = fp_int64ToFixed64(-fp_int_little_max);
  // return ((big * little) / (1 << fp_scale)); 
  return ((big * little) >> fp_scale);
}
