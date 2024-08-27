#include "maxl.h"

void MAXL::begin(void){
  // -------------------------------------------- queue needs some setup, 
  for(uint8_t i = 0; i < MAXL_QUEUE_SIZE; i ++){
    // and we link this -> next, prev <- this 
    if(i != MAXL_QUEUE_SIZE - 1) queue[i].next = &(queue[i+1]);
    if(i != 0) queue[i].prev = &(queue[i-1]);
  }
  // and the wraparound cases, 
  queue[0].prev = &(queue[MAXL_QUEUE_SIZE - 1]);
  queue[MAXL_QUEUE_SIZE - 1].next = &(queue[0]);
  head = &(queue[0]);  // where to write-in, 
  tail = &(queue[0]);  // which is ticking along... 
}

void MAXL::setInterval(uint8_t interval){
  // would we need to update anything ?
  intervalBitWidth = interval;
}

size_t MAXL::getQueueLength(void){
  size_t len = 0; 
  splinePt_t* ptr = tail;
  for(uint8_t i = 0; i < MAXL_QUEUE_SIZE; i ++){
    if(ptr == head) return len;
    len ++;
    ptr = ptr->next;
  }
  return len; 
}

void MAXL::addControlPoint(uint64_t timestamp, fxp32_16_t pt, maxlFlags_t flags){
  if (getQueueLength() + 2 > MAXL_QUEUE_SIZE){
    postErrorMessage("overfull");
    return; 
  } else if(flags.bits.isStreamStart) {
    // reset queue on start, 
    tail = &(queue[0]);
    head = &(queue[0]);
    streamActive = true; 
    postErrorMessage("startup");
  } else if(head->prev->time + (1 << intervalBitWidth) != timestamp){
    // sequences need to be continuous ! 
    postErrorMessage("missed segment, " + String((uint32_t)(head->prev->time)) + " " + String((uint32_t)(timestamp)));
    return;
  }

  // stash it, 
  head->time = timestamp;
  head->pt = pt;
  head->isLastPt = flags.bits.isStreamEnd;

  // advance the head pointer, 
  head = head->next;
}

static const fxp32_16_t one_sixth = fxp32_16_fromFloat(1.0F / 6.0F);
static const fxp32_16_t one_half = fxp32_16_fromFloat(1.0F / 2.0F);
static const fxp32_16_t two_thirds = fxp32_16_fromFloat(2.0F / 3.0F);

maxl_eval_t MAXL::evaluate(uint64_t timestamp){
  // noop if we're not running, 
  if(!streamActive) return { .pos = lastPtEvaluated, .isValid = false }; 

  // is queue-tail in the future?
  if(tail->time > timestamp) return { .pos = lastPtEvaluated, .isValid = false }; 

  // ok, goddamn, firstly, we flush the tail until it is one stamp's worth of time in the past, 
  for(uint8_t i = 0; i < MAXL_QUEUE_SIZE; i ++){
    if(getQueueLength() <= 4){
      // this is buffer starvation, 
      postErrorMessage("STARVED @ " + String((uint32_t)timestamp));
      return { .pos = lastPtEvaluated, .isValid = false };
    } else if (tail->time <= timestamp && tail->next->time <= timestamp){
      // increment and continue fwds, 
      tail = tail->next; 
    } else if (tail->time <= timestamp && tail->next->time > timestamp){
      // tail in correct position, carry on:
      break; 
    } else {
      postErrorMessage("oddball time state ... "); 
      // + String(getQueueLength()) + ", " + String((uint32_t)timestamp) + ", " + String((uint32_t)tail->time) + ", " + String((uint32_t)tail->next->time));
      return { .pos = lastPtEvaluated, .isValid = false }; 
    }
  }

  // handling end-of-streams, 
  if(tail->isLastPt){
    streamActive = false;
    return { .pos = lastPtEvaluated, .isValid = false }; 
  }

  splinePt_t * qp0 = tail->prev;
  splinePt_t * qp1 = tail;
  splinePt_t * qp2 = tail->next;
  splinePt_t * qp3 = tail->next->next;

  // what of our time base ? 
  // we have timestamp - qp1->time = microseconds-into-segment, 
  // and 0-1 being our time-base: 10...16 bit, 
  // if we have time-base of '10' we do no conversion, 
  // otherwise we have to upscale (?) 
  fxp32_16_t t = (timestamp - qp1->time) << (16 - intervalBitWidth); //fxp32_16_fromUInt32((timestamp - qp1->time) << (intervalBitWidth - 10));
  fxp32_16_t tt = fxp32_16_mult(t, t);
  fxp32_16_t ttt = fxp32_16_mult(tt, t);
  // lol step one is to get the params !
  // we do need some queue'en 
  fxp32_16_t p0 = qp0->pt;
  fxp32_16_t p1 = qp1->pt;
  fxp32_16_t p2 = qp2->pt;
  fxp32_16_t p3 = qp3->pt;

  // TODO: a ... d could be evaluated just once, before we start each chunk - then we just do the last multiplications... 
  fxp32_16_t a = fxp32_16_mult(one_sixth, p0) + fxp32_16_mult(two_thirds, p1) + fxp32_16_mult(one_sixth, p2);
  fxp32_16_t b = - fxp32_16_mult(one_half, p0) + fxp32_16_mult(one_half, p2);
  fxp32_16_t c = fxp32_16_mult(one_half, p0) - p1 + fxp32_16_mult(one_half, p2);
  fxp32_16_t d = - fxp32_16_mult(one_sixth, p0) + fxp32_16_mult(one_half, p1) - fxp32_16_mult(one_half, p2) + fxp32_16_mult(one_sixth, p3);

  // ... t, tt, ttt 
  lastPtEvaluated = a + fxp32_16_mult(b, t) + fxp32_16_mult(c, tt) + fxp32_16_mult(d, ttt);
  // postErrorMessage("t: " + String(fxp32_16_toFloat(t), 4)
  //             + ", p0: " + String(fxp32_16_toFloat(p0)) + ", p1: " + String(fxp32_16_toFloat(p1))  + ", p2: " + String(fxp32_16_toFloat(p2)) 
  //             + ", a: " + String(fxp32_16_toFloat(a)) // + ", b: " + String(fxp32_16_toFloat(b))
  //             );

  // postErrorMessage("t: " + String(fxp32_16_toFloat(t), 4)
  //             + ", p0: " + String(fxp32_16_toFloat(p0)) + ", 1/6, p1: " + String(fxp32_16_toFloat(fxp32_16_mult(one_sixth, p0)), 5)
  //             );

  return { .pos = lastPtEvaluated, .isValid = true }; 
}

float MAXL::getPosition(void){
  return fxp32_16_toFloat(lastPtEvaluated);
}

/*
def cubic_basis(t, params):
    p0, p1, p2, p3 = params 

    tt = t * t 
    ttt = tt * t 

    a = p0 + 4 * p1 + p2 
    b = - 3 * p0 + 3 * p2
    c = 3 * p0 - 6 * p1 + 3 * p2
    d = - p0 + 3 * p1 - 3 * p2 + p3

    return 1/6 * (a + b * t + c * tt + d * ttt)

# when we expand the 1/6 within (for less overflowey intermediate vals)

a = 1/6 * p0 + 2/3 * p1 + 1/6 * p2 
b = - 1/2 * p0 + 1/2 * p2
c = 1/2 * p0 - p1 + 1/2 * p2
d = - 1/6 * p0 + 1/2 * p1 - 1/2 * p2 + 1/6 * p3
*/

void MAXL::postErrorMessage(String msg){
  _errorMessage = msg;
  _errorFlag = true;
}

String MAXL::getErrorMessage(void){
  if(_errorFlag){
    _errorFlag = false;
    return _errorMessage;
  } else {
    return "";
  }
}