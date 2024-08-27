// randy bit gen 

#include "random_sequence_gen.h"

void randomGenAddChars(char* dest, size_t maxLen){
  size_t len = strlen(dest);
  if(len + 5 >= maxLen) len = maxLen - 5;
  dest[len ++] = '_';
  // seed random w/ timestamp - improvement would be unconnected ADC line or sth 
  srand((uint)micros());
  for(uint8_t c = 0; c < 5; c ++){
    int randNum = rand() % 26;
    dest[len + c] = randNum + 'a';
  }
  // finally, 
  dest[len + 5] = '\0';
}
