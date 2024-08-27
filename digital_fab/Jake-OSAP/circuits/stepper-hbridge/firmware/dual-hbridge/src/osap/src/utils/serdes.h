#ifndef OSAP_SERDES_H_
#define OSAP_SERDES_H_ 

#include "serdes_keys.h"

// --------------------------  
// TODO: write serializeSafe() versions, which stash (and check for) keys ! 
// TODO: serializers should be length-guarded: serializeTight(var, buffer, wptr, maxsize)
//       ... they could simply stop writing in those cases 

// --------------------------  Base Cases

template<typename T>
void serializeTight(T var, uint8_t* buffer, size_t* wptr){
  static_assert(is_supported_type<T>::value, "One of the types you are trying to serialize \
is not included in OSAP's type set. Please use only standard C types.");
}

template<typename T>
T deserializeTight(uint8_t* buffer, size_t* rptr){
  static_assert(is_supported_type<T>::value, "One of the types you are trying to deserialize \
is not included in OSAP's type set. Please use only standard C types.");
}

// --------------------------  Boolean

template<>inline 
void serializeTight<bool>(bool var, uint8_t* buffer, size_t* wptr){
  buffer[*wptr] = var ? 1 : 0;
  (*wptr) ++;
}

template<>inline 
bool deserializeTight<bool>(uint8_t* buffer, size_t* rptr){
  bool result = buffer[*rptr];
  (*rptr) ++;
  return result; 
}

// -------------------------- Serialize Signed Integers 


template<>inline 
void serializeTight<int8_t>(int8_t var, uint8_t* buffer, size_t* wptr){
  buffer[*wptr] = var; 
  (*wptr) ++;
}

template<>inline 
void serializeTight<int16_t>(int16_t var, uint8_t* buffer, size_t* wptr){
  size_t offset = *wptr;
  buffer[offset ++] = var & 255;
  buffer[offset ++] = (var >> 8) & 255;
  *wptr = offset;
}

template<>inline 
void serializeTight<int32_t>(int32_t var, uint8_t* buffer, size_t* wptr){
  size_t offset = *wptr;
  buffer[offset ++] = var & 255;
  buffer[offset ++] = (var >> 8) & 255;
  buffer[offset ++] = (var >> 16) & 255;
  buffer[offset ++] = (var >> 24) & 255;
  *wptr = offset;
}

template<>inline 
void serializeTight<int64_t>(int64_t var, uint8_t* buffer, size_t* wptr){
  size_t offset = *wptr;
  buffer[offset ++] = var & 255;
  buffer[offset ++] = (var >> 8) & 255;
  buffer[offset ++] = (var >> 16) & 255;
  buffer[offset ++] = (var >> 24) & 255;
  buffer[offset ++] = (var >> 32) & 255;
  buffer[offset ++] = (var >> 40) & 255;
  buffer[offset ++] = (var >> 48) & 255;
  buffer[offset ++] = (var >> 56) & 255;
  *wptr = offset; 
}

// -------------------------- Deserialize Signed Integers 

template<>inline
int8_t deserializeTight<int8_t>(uint8_t* buffer, size_t* rptr){
  int8_t result = buffer[*rptr];
  (*rptr) ++;
  return result; 
}


template<>inline 
int16_t deserializeTight<int16_t>(uint8_t* buffer, size_t* rptr){
  int16_t result = 0;
  size_t offset = *rptr;
  result |= static_cast<int16_t>(buffer[offset ++]);
  result |= static_cast<int16_t>(buffer[offset ++]) << 8;
  *rptr = offset; 
  return result;  
}

template<>inline 
int32_t deserializeTight<int32_t>(uint8_t* buffer, size_t* rptr){
  int32_t result = 0;
  size_t offset = *rptr;
  result |= static_cast<int32_t>(buffer[offset ++]);
  result |= static_cast<int32_t>(buffer[offset ++]) << 8;
  result |= static_cast<int32_t>(buffer[offset ++]) << 16;
  result |= static_cast<int32_t>(buffer[offset ++]) << 24;
  *rptr = offset; 
  return result;  
}

template<>inline 
int deserializeTight<int>(uint8_t* buffer, size_t* rptr){
  return deserializeTight<int32_t>(buffer, rptr);
}

template<>inline 
int64_t deserializeTight<int64_t>(uint8_t* buffer, size_t* rptr){
  int64_t result = 0;
  size_t offset = *rptr; 
  result |= static_cast<int64_t>(buffer[offset ++]);
  result |= static_cast<int64_t>(buffer[offset ++]) << 8;
  result |= static_cast<int64_t>(buffer[offset ++]) << 16;
  result |= static_cast<int64_t>(buffer[offset ++]) << 24;
  result |= static_cast<int64_t>(buffer[offset ++]) << 32;
  result |= static_cast<int64_t>(buffer[offset ++]) << 40;
  result |= static_cast<int64_t>(buffer[offset ++]) << 48;
  result |= static_cast<int64_t>(buffer[offset ++]) << 56;
  *rptr = offset; 
  return result;
}

// --------------------------  Serialize Unsigned Integers 

template<>inline 
void serializeTight<uint8_t>(uint8_t var, uint8_t* buffer, size_t* wptr){
  buffer[*wptr] = var; 
  (*wptr) ++;
}

template<>inline 
void serializeTight<uint16_t>(uint16_t var, uint8_t* buffer, size_t* wptr){
  size_t offset = *wptr;
  buffer[offset ++] = var & 255;
  buffer[offset ++] = (var >> 8) & 255;
  *wptr = offset;
}

template<>inline 
void serializeTight<uint32_t>(uint32_t var, uint8_t* buffer, size_t* wptr){
  size_t offset = *wptr;
  buffer[offset ++] = var & 255;
  buffer[offset ++] = (var >> 8) & 255;
  buffer[offset ++] = (var >> 16) & 255;
  buffer[offset ++] = (var >> 24) & 255;
  *wptr = offset;
}

template<>inline 
void serializeTight<uint64_t>(uint64_t var, uint8_t* buffer, size_t* wptr){
  size_t offset = *wptr;
  buffer[offset ++] = var & 255;
  buffer[offset ++] = (var >> 8) & 255;
  buffer[offset ++] = (var >> 16) & 255;
  buffer[offset ++] = (var >> 24) & 255;
  buffer[offset ++] = (var >> 32) & 255;
  buffer[offset ++] = (var >> 40) & 255;
  buffer[offset ++] = (var >> 48) & 255;
  buffer[offset ++] = (var >> 56) & 255;
  *wptr = offset; 
}

// --------------------------  Deserialize Unsigned Integers 

template<>inline
uint8_t deserializeTight<uint8_t>(uint8_t* buffer, size_t* rptr){
  uint8_t result = buffer[*rptr];
  (*rptr) ++;
  return result; 
}

template<>inline 
uint16_t deserializeTight<uint16_t>(uint8_t* buffer, size_t* rptr){
  uint16_t result = 0;
  size_t offset = *rptr;
  result |= static_cast<uint16_t>(buffer[offset ++]);
  result |= static_cast<uint16_t>(buffer[offset ++]) << 8;
  *rptr = offset; 
  return result;
}

template<>inline 
uint32_t deserializeTight<uint32_t>(uint8_t* buffer, size_t* rptr){
  uint32_t result = 0;
  size_t offset = *rptr;
  result |= static_cast<uint32_t>(buffer[offset ++]);
  result |= static_cast<uint32_t>(buffer[offset ++]) << 8;
  result |= static_cast<uint32_t>(buffer[offset ++]) << 16;
  result |= static_cast<uint32_t>(buffer[offset ++]) << 24;
  *rptr = offset; 
  return result;
}

template<>inline 
uint64_t deserializeTight<uint64_t>(uint8_t* buffer, size_t* rptr){
  uint64_t result = 0;
  size_t offset = *rptr; 
  result |= static_cast<uint64_t>(buffer[offset ++]);
  result |= static_cast<uint64_t>(buffer[offset ++]) << 8;
  result |= static_cast<uint64_t>(buffer[offset ++]) << 16;
  result |= static_cast<uint64_t>(buffer[offset ++]) << 24;
  result |= static_cast<uint64_t>(buffer[offset ++]) << 32;
  result |= static_cast<uint64_t>(buffer[offset ++]) << 40;
  result |= static_cast<uint64_t>(buffer[offset ++]) << 48;
  result |= static_cast<uint64_t>(buffer[offset ++]) << 56;
  *rptr = offset; 
  return result;
}

// -------------------------- Serdes Floats  

union union_float {
  uint8_t bytes[4];
  float f;
};

union union_double {
  uint8_t bytes[8];
  double d;
};


template<>inline
void serializeTight<float>(float var, uint8_t* buffer, size_t* wptr){
  union_float union_f;
  union_f.f = var;
  size_t offset = *wptr;
  buffer[offset ++] = union_f.bytes[0]; 
  buffer[offset ++] = union_f.bytes[1]; 
  buffer[offset ++] = union_f.bytes[2]; 
  buffer[offset ++] = union_f.bytes[3]; 
  *wptr = offset; 
}

template<>inline 
float deserializeTight<float>(uint8_t* buffer, size_t* rptr){
  size_t offset = *rptr;
  union_float union_f = {
    .bytes = {
      buffer[offset ++],
      buffer[offset ++],
      buffer[offset ++],
      buffer[offset ++],
    }
  };
  *rptr = offset; 
  return union_f.f;
}

template<>inline
void serializeTight<double>(double var, uint8_t* buffer, size_t* wptr){
  union_double union_d;
  union_d.d = var;
  size_t offset = *wptr;
  buffer[offset ++] = union_d.bytes[0]; 
  buffer[offset ++] = union_d.bytes[1]; 
  buffer[offset ++] = union_d.bytes[2]; 
  buffer[offset ++] = union_d.bytes[3]; 
  buffer[offset ++] = union_d.bytes[4]; 
  buffer[offset ++] = union_d.bytes[5]; 
  buffer[offset ++] = union_d.bytes[6]; 
  buffer[offset ++] = union_d.bytes[7]; 
  *wptr = offset; 
}

template<>inline 
double deserializeTight<double>(uint8_t* buffer, size_t* rptr){
  size_t offset = *rptr;
  union_double union_d = {
    .bytes = {
      buffer[offset ++],
      buffer[offset ++],
      buffer[offset ++],
      buffer[offset ++],
      buffer[offset ++],
      buffer[offset ++],
      buffer[offset ++],
      buffer[offset ++],
    }
  };
  *rptr = offset; 
  return union_d.d;
}

// -------------------------- Serdes Strings

template<>inline 
void serializeTight<String>(String var, uint8_t* buffer, size_t* wptr){
  size_t len = var.length(); 
  if(len > 128) len = 128; 
  buffer[(*wptr) ++] = len;
  for(uint8_t i = 0; i < len; i ++){
    buffer[(*wptr) ++] = var.charAt(i);
  } 
}

template<>inline 
void serializeTight<char*>(char* var, uint8_t* buffer, size_t* wptr){
  // buffer[(*wptr) ++] = TYPEKEY_STRING;
  size_t len = strlen(var);
  buffer[(*wptr) ++] = len;
  // this should copy the string but not its trailing zero, 
  memcpy(&(buffer[*wptr]), var, len);
  (*wptr) += len;
}

// fk it, we can expose our serialized 'string' as an arduino String 
// for convenience / familiarity... nothing in-system uses this, so 
// flash shouldn't be affected until it's invoked by i.e. autoRPC w/ String args 
template<>inline 
String deserializeTight<String>(uint8_t* buffer, size_t* rptr){
  // swappable buffer 
  static char string_stash[256] = { 'h', 'e', 'l', 'l', 'o' };
  // otherwise we have this len to unpack:
  size_t len = buffer[(*rptr)];
  // copy those into our stash and stuff a null terminator: 
  memcpy(string_stash, buffer + (*rptr) + 1, len);
  string_stash[len] = '\0';
  // don't forget to increment the rptr accordingly
  *rptr += len + 1;
  // a new String, on the stack, to return: 
  return string_stash;
  // return String(string_stash);
}

// to deserialize char*, we use a different API where we deserialize straight 
// into an available variable... which it should be possible to do for any type fwiw,
// and maybe a good TODO if we want to save some cycles etc ? 

template<typename T>
void deserializeTightInto(T dest, uint8_t* buffer, size_t* rptr, size_t maxLen){}

template<>inline
void deserializeTightInto<char*>(char* dest, uint8_t* buffer, size_t* rptr, size_t maxLen){
  // the byte at [rptr] denotes length of the incoming string, 
  size_t len = buffer[(*rptr)];
  if(len >= maxLen) len = maxLen - 1;
  // copy-into, and append the delimeter 
  memcpy(dest, buffer + (*rptr) + 1, len);
  dest[len] = '\0';
  // deserializers expect their read-pointers incremented 
  *rptr += len;
}

#endif 