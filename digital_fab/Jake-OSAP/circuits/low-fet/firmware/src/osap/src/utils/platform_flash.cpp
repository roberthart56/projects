#include "platform_flash.h"
#include "../osap_config.h"

// TODO: better per-platform guards, 
// i.e. compile-time error "looks like your core is not supported..."
// and FlashStorage_SAMD should be explicit #if defined(SAMD21...)
#if defined(ARDUINO_ARCH_MBED_RP2040) || defined(ARDUINO_ARCH_RP2040) || defined(ARDUINO_TEENSY41) || defined(ARDUINO_TEENSY40)
#include <EEPROM.h>
#else
#include <FlashStorage_SAMD.h>
#endif

const int MAGIC_SIGGY = 0xBEEFDEED;
const int STORAGE_ADDR = 0;
char tempChars[OSAP_PROPERNAMES_MAX_CHAR];
int storedSignature;

void flashBegin(void){
  #if defined(ARDUINO_ARCH_MBED_RP2040) || defined(ARDUINO_ARCH_RP2040)
  EEPROM.begin(4096);
  #elif defined(ARDUINO_TEENSY41) || defined(ARDUINO_TEENSY40)
  EEPROM.begin();
  #endif 
}

bool flashNameStorageCheck(void){
  EEPROM.get(STORAGE_ADDR, storedSignature);
  return storedSignature == MAGIC_SIGGY;
}

void flashCopySavedNameInto(char* dest){
  EEPROM.get(STORAGE_ADDR + sizeof(storedSignature), tempChars);
  strncpy(dest, tempChars, OSAP_PROPERNAMES_MAX_CHAR);
  dest[OSAP_PROPERNAMES_MAX_CHAR - 1] = '\0';
}

void flashSaveName(char* source){
  strncpy(tempChars, source, OSAP_PROPERNAMES_MAX_CHAR);
  tempChars[OSAP_PROPERNAMES_MAX_CHAR - 1] = '\0';
  EEPROM.put(STORAGE_ADDR, MAGIC_SIGGY);
  EEPROM.put(STORAGE_ADDR + sizeof(storedSignature), tempChars);
  // seems as though this is and earle-only ? or it aint in the teensy, 
  // and it aint in the docs: https://docs.arduino.cc/learn/built-in-libraries/eeprom/
  #if defined(ARDUINO_ARCH_MBED_RP2040) || defined(ARDUINO_ARCH_RP2040)
  EEPROM.commit();
  #elif defined(ARDUINO_TEENSY41) || defined(ARDUINO_TEENSY40)
  // EEPROM.commit();
  #else 
  EEPROM.commit();
  #endif 
}