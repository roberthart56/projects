#ifndef PLATFORM_SPECIFICS_H_
#define PLATFORM_SPECIFICS_H_

// at the moment, just flash codes per platform 

#include <Arduino.h>

void flashBegin(void);
bool flashNameStorageCheck(void);
void flashCopySavedNameInto(char* dest);
void flashSaveName(char* name);

#endif 