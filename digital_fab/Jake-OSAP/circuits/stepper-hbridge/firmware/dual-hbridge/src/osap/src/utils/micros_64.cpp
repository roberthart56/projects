#include "micros_64.h"

uint32_t lastMicros = 0;
uint64_t overflows = 0;

uint64_t micros64(void){

  // TODO: don't trust arduino's micros() - it goes backwards - forreal - sometimes 
  // meaning that we need this threshold value... 
  uint32_t currentMicros = micros();

  if(currentMicros < lastMicros && (lastMicros - currentMicros) > 1000000){
    overflows ++;
  }

  lastMicros = currentMicros; 

  return (overflows << 32) | currentMicros;
}