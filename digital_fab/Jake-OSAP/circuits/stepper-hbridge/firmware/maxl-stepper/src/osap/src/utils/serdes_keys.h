#ifndef OSAP_SERDES_KEYS_H_
#define OSAP_SERDES_KEYS_H_

#include <Arduino.h>
#include <type_traits>

// --------------------------  Key Codes 

//                      dec    name   bin          dec
#define TYPEKEY_NULL    0   // null   0b00000000     0
#define TYPEKEY_BOOL    1   // bool   0b00000001     1 
#define TYPEKEY_UNKNWN  3   // unknwn 0b00000011     3 

#define TYPEKEY_I8      16  // i8     0b00010000    16
#define TYPEKEY_I16     17  // i16    0b00010001    17
#define TYPEKEY_I32     18  // i32    0b00010010    18
#define TYPEKEY_I64     19  // i64    0b00010011    19
#define TYPEKEY_I128    20  // i128   0b00010100    20

#define TYPEKEY_U8      24  // u8     0b00011000    24
#define TYPEKEY_U16     25  // u16    0b00011001    25
#define TYPEKEY_U32     26  // u32    0b00011010    26
#define TYPEKEY_U64     27  // u64    0b00011011    27
#define TYPEKEY_U128    28  // u128   0b00011100    28

#define TYPEKEY_F16     33  // f16    0b00100001    33
#define TYPEKEY_F32     34  // f32    0b00100010    34
#define TYPEKEY_F64     35  // f64    0b00100011    35
#define TYPEKEY_F128    36  // f128   0b00100100    36

#define TYPEKEY_ASCII   48  // ascii  0b00110000    48
#define TYPEKEY_UTF8    49  // utf8   0b00110001    49 

#define TYPEKEY_ARRY    64  // arry   0b01000000    64
#define TYPEKEY_TNSR    65  // tnsr   0b01000001    65

// --------------------------  We declare a unit type, for void-passers

struct Unit{};
constexpr Unit unit{};

// --------------------------  Key Getters w/ Existence Checkers 

// ---------------- Unknowns:

template<typename T>
struct is_supported_type : std::false_type {};

// the default / unspecialized will deploy when we have 
// an unknown key: since we don't have codes for those, we should throw a 
// compile time error 
template<typename T>
uint8_t getTypeKey(void){
static_assert(is_supported_type<T>::value, "One of the types you have deployed as a function return, \
or as an argument, is not included in OSAP's type set. Please use only standard C types.");
  return TYPEKEY_UNKNWN;
}

// ---------------- Null / Void:

template<>
struct is_supported_type<Unit> : std::true_type {};

template<>
struct is_supported_type<void> : std::true_type {};

template<> inline
uint8_t getTypeKey<Unit>(void){
  return TYPEKEY_NULL;
}

template<> inline
uint8_t getTypeKey<void>(void){
  return TYPEKEY_NULL;
}

// ---------------- Boolean:

template<>
struct is_supported_type<bool> : std::true_type {};

template<> inline
uint8_t getTypeKey<bool>(void){
  return TYPEKEY_BOOL;
}

// ---------------- Signed Integers:

template<>
struct is_supported_type<int8_t> : std::true_type {};

template<>
struct is_supported_type<int16_t> : std::true_type {};

template<>
struct is_supported_type<int32_t> : std::true_type {};

template<>
struct is_supported_type<int> : std::true_type {};

template<>
struct is_supported_type<int64_t> : std::true_type {};

template<> inline 
uint8_t getTypeKey<int8_t>(void){
  return TYPEKEY_I8;
}

template<> inline 
uint8_t getTypeKey<int16_t>(void){
  return TYPEKEY_I16;
}

template<> inline 
uint8_t getTypeKey<int32_t>(void){
  return TYPEKEY_I32;
}

template<> inline 
uint8_t getTypeKey<int>(void){
  return TYPEKEY_I32;
}

template<> inline 
uint8_t getTypeKey<int64_t>(void){
  return TYPEKEY_I64;
}

// ---------------- Unsigned Integers:

template<>
struct is_supported_type<uint8_t> : std::true_type {};

template<>
struct is_supported_type<uint16_t> : std::true_type {};

template<>
struct is_supported_type<uint32_t> : std::true_type {};

template<>
struct is_supported_type<uint64_t> : std::true_type {};

template<> inline 
uint8_t getTypeKey<uint8_t>(void){
  return TYPEKEY_U8;
}

template<> inline 
uint8_t getTypeKey<uint16_t>(void){
  return TYPEKEY_U16;
}

template<> inline 
uint8_t getTypeKey<uint32_t>(void){
  return TYPEKEY_U32;
}

template<> inline 
uint8_t getTypeKey<uint64_t>(void){
  return TYPEKEY_U64;
}

// ---------------- Floats:

template<>
struct is_supported_type<float> : std::true_type {};

template<>
struct is_supported_type<double> : std::true_type {};

template<> inline
uint8_t getTypeKey<float>(void){
  return TYPEKEY_F32;
}

template<> inline
uint8_t getTypeKey<double>(void){
  return TYPEKEY_F64;
}

// ---------------- Strings:

template<>
struct is_supported_type<char*> : std::true_type {};

template<>
struct is_supported_type<String> : std::true_type {};

template<> inline 
uint8_t getTypeKey<char*>(void){
  return TYPEKEY_UTF8;
}
template<> inline
uint8_t getTypeKey<String>(void){
  return TYPEKEY_UTF8;
}

#endif 