#ifndef MOTION_STATE_MACHINE_H_
#define MOTION_STATE_MACHINE_H_

#include <Arduino.h>
#include <hardware/timer.h>
#include <hardware/irq.h>

#define MOTION_MODE_POS           0
#define MOTION_MODE_VEL           1

// units here area always full steps, 
// i.e. 200 steps per revolution (for a typical stepper) 
// but we effectively do 512 microsteps internally
// (one full electrical phase is 2048 ticks of a LUT) 

typedef struct motionState_t {
  float pos;
  float vel;
  float accel;
} motionState_t;

void motion_init(uint32_t microsecondsPerIntegration);

void motion_integrate(void);
void alarm_dt_handler(void);

void motion_setPositionTarget(float target, float maxVel, float maxAccel);
void motion_setVelocityTarget(float target, float maxAccel);
void motion_setPosition(float pos);

void motion_getCurrentStates(motionState_t* statePtr);
String motion_getErrorMessage(void);

#endif 
