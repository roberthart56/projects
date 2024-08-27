/*
osap/routes.cpp

directions

Jake Read at the Center for Bits and Atoms
(c) Massachusetts Institute of Technology 2021

This work may be reproduced, modified, distributed, performed, and
displayed for any purpose, but must acknowledge the osap project.
Copyright is retained and must be preserved. The work is provided as is;
no warranty is provided, and users accept all liability.
*/

#include "routes.h"
#include "../utils/keys.h"
// #include "../utils/serdes.h"
#include "../utils/debug.h"

// Route::Route(void){

// }

// direct constructor, 
// although TODO: it's unclear if this is a useful or used semantic, 
// since string-masking... so I will delete until we are testing 
/*
Route::Route(uint8_t* _encodedPath, uint16_t _encodedPathLen, uint16_t _timeToLive, uint16_t _maxSegmentSize){
// guard, should do better to stash / report errors, idk 
  if(_encodedPathLen > 64){
    _encodedPathLen = 64;
  }
  // copy-in 
  timeToLive = _timeToLive;
  maxSegmentSize = _maxSegmentSize;
  encodedPathLen = _encodedPathLen;
  // memcpy-in 
  memcpy(encodedPath, _encodedPath, encodedPathLen);
}

// empty constructor for chaining, 
Route::Route(void){}

Route* Route::linkf(uint8_t txIndex){
  encodedPath[encodedPathLen ++] = PKEY_LFWD << 6 | (txIndex & 0b00011111);
  return this;
}

Route* Route::busf(uint8_t txIndex, uint8_t txAddress){
  encodedPath[encodedPathLen ++] = PKEY_BFWD << 6 | (txIndex & 0b00011111);
  encodedPath[encodedPathLen ++] = txAddress;
  return this;
}

Route* Route::end(uint16_t _timeToLive, uint16_t _maxSegmentSize){
  timeToLive = _timeToLive;
  maxSegmentSize = _maxSegmentSize;
  return this;
}
*/

// TODO: it seems like (?) we could shave this chunk of RAM 
// by using some other temporary buffer, like the Port::payload or Port::datagram 
// but would need to analyze whether / not those are likely to be mid-write 
// when this is called (which actually seems fairly likely) 
uint8_t oldPathStash[OSAP_CONFIG_ROUTE_MAX_LENGTH];

void Route::reverse(void){
  // pull a copy of the path out, 
  memcpy(oldPathStash, encodedPath, encodedPathLen);
  // reading from 1st-key in old, writing from back-to-front into new, 
  uint8_t rptr = 0;
  uint8_t wptr = encodedPathLen; 
  while(wptr > 0){
    // protocol is such that PKEY == size of that instruction
    uint8_t increment = oldPathStash[rptr] >> 6;
    if(!increment || increment == 3){
      OSAP_ERROR("route-reversal key badness");
      increment = 2;
    }
    wptr -= increment;
    for(uint8_t i = 0; i < increment; i ++){
      encodedPath[wptr + i] = oldPathStash[rptr + i];
    }
    rptr += increment;
  }
}

void Route::reset(void){
  encodedPathLen = 0;
}

void Route::addLink(uint8_t index){
  encodedPath[encodedPathLen ++] = PKEY_LFWD << 6 | (index & 0b00011111);
}

void Route::setTimeToLive(uint16_t microseconds){
  timeToLive = microseconds;
}

void Route::setMaxSegmentSize(uint16_t byteCount){
  maxSegmentSize = byteCount; 
}
