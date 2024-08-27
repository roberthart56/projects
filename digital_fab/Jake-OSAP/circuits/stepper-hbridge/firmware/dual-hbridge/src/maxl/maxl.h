#ifndef MAXL_H_
#define MAXL_H_

#include <Arduino.h>
#include "fxp.h"

#define MAXL_QUEUE_SIZE 128

typedef struct splinePt_t {
  fxp32_16_t pt;
  // microseconds 
  uint64_t time;
  bool isLastPt = false; 
  splinePt_t* next;
  splinePt_t* prev;
} splinePt_t;

union maxlFlags_t {
    struct {
        unsigned int isStreamStart : 1;
        unsigned int isStreamEnd : 1;
    } bits;
    unsigned char byte;
};

typedef struct maxl_eval_t {
  fxp32_16_t pos;
  bool isValid; 
} maxl_eval_t;

class MAXL {
  public:
    void begin(void);
    void setInterval(uint8_t interval);
    void addControlPoint(uint64_t timestamp, fxp32_16_t pt, maxlFlags_t flags = { .byte = 0 });
    maxl_eval_t evaluate(uint64_t timestamp);
    float getPosition(void);
    String getErrorMessage(void);

  private:
    // is num. bits for the interval period, microseconds, 
    uint8_t intervalBitWidth = 0;
    // streaming-or-not, and last eval'd 
    bool streamActive = false; 
    fxp32_16_t lastPtEvaluated = 0;
    void postErrorMessage(String msg);
    String _errorMessage;
    bool _errorFlag = false; 
    // will we need to stash pts-times ? 
    splinePt_t queue[MAXL_QUEUE_SIZE];
    splinePt_t* head = 0;
    splinePt_t* tail = 0; 
    // queue mgmt 
    size_t getQueueLength(void);
};  

#endif 