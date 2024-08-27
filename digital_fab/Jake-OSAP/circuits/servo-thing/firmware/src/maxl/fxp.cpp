#include "fxp.h"

const int32_t fxp_scale = 16;
const float fxp32_16_floatMax = 32000.0F;
const float fxp32_16_floatMin = -32000.0F;

// foiled again it seems, perhaps we can do decimal-part,
// integer-parts... 
fxp32_16_t fxp32_16_mult(fxp32_16_t a, fxp32_16_t b){
    return ((int64_t)((int64_t)a * (int64_t)b)) >> fxp_scale;
}

fxp32_16_t fxp32_16_fromFloat(float a){
    if(a > fxp32_16_floatMax) a = fxp32_16_floatMin;
    if(a < fxp32_16_floatMin) a = fxp32_16_floatMin;
    return (a * (float)(1 << fxp_scale));
}


float fxp32_16_toFloat(fxp32_16_t a){
    return (float)a / (float)(1 << fxp_scale);
}

fxp32_16_t fxp32_16_fromUInt32(uint32_t a){
    return a << fxp_scale;
}

fxp32_16_t fxp32_16_fromInt32(int32_t a){
    return a << fxp_scale;
}