import struct
from typing import Tuple 

#                       dec    name   bin          dec
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

# keys for proper type names, 
TypeKeys = {
    'null':     0,
    'bool':     1,
    'unknwn':   3, 
    'i8':       16,
    'i16':      17,
    'i32':      18,
    'i64':      19,
    'i128':     20,
    'u8':       24,
    'u16':      25,
    'u32':      26,
    'u64':      27,
    'u128':     28,
    'f16':      33,
    'f32':      34,
    'f64':      35,
    'f128':     36,
    'ascii':    48,
    'utf8':     49,
    'arry':     64,
    'tnsr':     65,
}

# serves as a conversion map as well, 
PythonicNames = {
    'None':     [0],
    'bool':     [1],
    # 'error':    3,  # if we tried to get a python name for this something has gone wrong 
    # 'int':       16,
    'int':      [17, 18, 19, 24, 25, 26, 27],
    # 'i128':     20, # idk about these yet 
    # 'u128':     28, 
    'float':    [33, 34, 35],
    # 'f128':     36,
    # 'ascii':    48,
    'str':      [49],
    # 'arry':     64, # not happening yet 
    # 'tnsr':     65,
}

# TODO: rm this, replace with deserialize_tight_... returning tuples of val, length... 
TypeLengths = {
    'void': 0, 
    'int': 4, 
    'bool': 2, 
    'float': 4,
}

def typekey_to_name(k: int) -> str:
    for name in TypeKeys:
        if TypeKeys[name] == k:
            return name 
    
    raise Exception(f"no name exists for the typekey {k}, consult the table in this file?")

def typekey_to_pythonic_name(k: int) -> str:
    for name in PythonicNames:
        for key in PythonicNames[name]:
            if key == k:
                return name 
        
    raise Exception(f"no pythonic name exists for the typekey {k}, consult the table in this file?")

# ------------------------------------- Empty

def deserialize_tight_null(source: bytearray, offset: int) -> Tuple[None, int]:
    return (None, 0) 

# ------------------------------------- Boolean 

def serialize_tight_bool(value: bool, dest: bytearray, offset: int):
    dest[offset] = int(value)
    return 1

def deserialize_tight_bool(source: bytearray, offset: int) -> Tuple[bool, int]:
    return (bool(source[offset]), 1)


# ------------------------------------- Signed Integers  

def serialize_tight_i8(value: int, dest: bytearray, offset: int):
    # as it happens, struct.pack will throw these erros for us, 
    # if value > (2 ** 7 - 1) or value < (-1 * 2 ** 7 + 1):
    #     raise ValueError(f"val of {value} written to int8 width")
    dest[offset:offset + 1] = struct.pack('<b', value)
    return 1

def serialize_tight_i16(value: int, dest: bytearray, offset: int):
    # if value > (2 ** 15 - 1) or value < (-1 * 2 ** 15 + 1):
    #     raise ValueError(f"val of {value} written to int16 width")
    dest[offset:offset + 2] = struct.pack('<h', value)
    return 2

def serialize_tight_i32(value: int, dest: bytearray, offset: int):
    # if value > (2 ** 31 - 1) or value < (-1 * 2 ** 31 + 1):
    #     raise ValueError(f"val of {value} written to int32 width")
    dest[offset:offset + 4] = struct.pack('<i', value)
    return 4

def serialize_tight_i64(value: int, dest: bytearray, offset: int):
    # if value > (2 ** 63 - 1) or value < (-1 * 2 ** 63 + 1):
    #     raise ValueError(f"val of {value} written to int64 width")
    dest[offset:offset + 8] = struct.pack('<q', value)
    return 8

def deserialize_tight_i8(source: bytearray, offset: int) -> Tuple[int, int]:
    return (struct.unpack('<b', source[offset:offset + 1])[0], 1)

def deserialize_tight_i16(source: bytearray, offset: int) -> Tuple[int, int]:
    return (struct.unpack('<h', source[offset:offset + 2])[0], 2)

def deserialize_tight_i32(source: bytearray, offset: int) -> Tuple[int, int]:
    return (struct.unpack('<i', source[offset:offset + 4])[0], 4)

def deserialize_tight_i64(source: bytearray, offset: int) -> Tuple[int, int]:
    return (struct.unpack('<q', source[offset:offset + 8])[0], 8)


# ------------------------------------- Unsigned Integers  

def serialize_tight_u8(value: int, dest: bytearray, offset: int):
    # if value > (2 ** 8 - 1) or value < 0:
    #     raise ValueError(f"val of {value} written to uint8")
    dest[offset:offset + 1] = struct.pack('<B', value)
    return 1 

def serialize_tight_u16(value: int, dest: bytearray, offset: int):
    # if value > (2 ** 16 - 1) or value < 0:
    #     raise ValueError(f"val of {value} written to uint16")
    dest[offset:offset + 2] = struct.pack('<H', value)
    return 2

def serialize_tight_u32(value: int, dest: bytearray, offset: int):
    # if value > (2 ** 32 - 1) or value < 0:
    #     raise ValueError(f"val of {value} written to uint32")
    dest[offset:offset + 4] = struct.pack('<I', value)
    return 4 

def serialize_tight_u64(value: int, dest: bytearray, offset: int):
    # if value > (2 ** 64 - 1) or value < 0:
    #     raise ValueError(f"value of {value} written to uint64")
    dest[offset:offset + 8] = struct.pack('<Q', value)
    return 8

def deserialize_tight_u8(source: bytearray, offset: int) -> Tuple[int, int]:
    return (struct.unpack('<B', source[offset:offset + 1])[0], 1)

def deserialize_tight_u16(source: bytearray, offset: int) -> Tuple[int, int]:
    return (struct.unpack('<H', source[offset:offset + 2])[0], 2)

def deserialize_tight_u32(source: bytearray, offset: int) -> Tuple[int, int]:
    return (struct.unpack('<I', source[offset:offset + 4])[0], 4)

def deserialize_tight_u64(source: bytearray, offset: int) -> Tuple[int, int]:
    return (struct.unpack('<Q', source[offset:offset + 8])[0], 8) 


# ------------------------------------- Floats  

def serialize_tight_f32(value: float, dest: bytearray, offset: int):
    dest[offset:offset + 4] = struct.pack('<f', value)
    return 4

def serialize_tight_f64(value: float, dest: bytearray, offset: int):
    dest[offset:offset + 8] = struct.pack('<d', value)
    return 8 

def deserialize_tight_f32(source: bytearray, offset: int) -> Tuple[float, int]:
    return (struct.unpack('<f', source[offset:offset + 4])[0], 4)

def deserialize_tight_f64(source: bytearray, offset: int) -> Tuple[float, int]:
    return (struct.unpack('<d', source[offset:offset + 8])[0], 8) 


# ------------------------------------- Strings

def serialize_tight_utf8(value: str, dest: bytearray, offset: int):
    string_encoded = value.encode('utf-8')
    dest[offset] = len(string_encoded)
    dest[offset + 1:offset + 1 + len(string_encoded)] = string_encoded
    return len(string_encoded) + 1

def deserialize_tight_utf8(source: bytearray, offset: int) -> Tuple[str, int]:
    # print("offset, source: ", offset, source)
    length = source[offset]
    return (source[offset + 1:offset + 1 + length].decode('utf-8'), length + 1)


# ------------------------------------- Switches

# call them by their (proper) names 

serialize_tight_switch = {
    # 'null':     serialize_tight_,
    'bool':     serialize_tight_bool,
    # 'unknwn':   serialize_tight_, 
    'i8':       serialize_tight_i8,
    'i16':      serialize_tight_i16,
    'i32':      serialize_tight_i32,
    'i64':      serialize_tight_i64,
    # 'i128':     serialize_tight_,
    'u8':       serialize_tight_u8,
    'u16':      serialize_tight_u16,
    'u32':      serialize_tight_u32,
    'u64':      serialize_tight_u64,
    # 'u128':     serialize_tight_,
    # 'f16':      serialize_tight_,
    'f32':      serialize_tight_f32,
    'f64':      serialize_tight_f64,
    # 'f128':     serialize_tight_,
    # 'ascii':    serialize_tight_,
    'utf8':     serialize_tight_utf8,
    # 'arry':     serialize_tight_,
    # 'tnsr':     serialize_tight_,
}

deserialize_tight_switch = {
    'null':     deserialize_tight_null,
    'bool':     deserialize_tight_bool,
    # 'unknwn':   deserialize_tight_, 
    'i8':       deserialize_tight_i8,
    'i16':      deserialize_tight_i16,
    'i32':      deserialize_tight_i32,
    'i64':      deserialize_tight_i64,
    # 'i128':     deserialize_tight_,
    'u8':       deserialize_tight_u8,
    'u16':      deserialize_tight_u16,
    'u32':      deserialize_tight_u32,
    'u64':      deserialize_tight_u64,
    # 'u128':     deserialize_tight_,
    # 'f16':      deserialize_tight_,
    'f32':      deserialize_tight_f32,
    'f64':      deserialize_tight_f64,
    # 'f128':     deserialize_tight_,
    # 'ascii':    deserialize_tight_,
    'utf8':     deserialize_tight_utf8,
    # 'arry':     deserialize_tight_,
    # 'tnsr':     deserialize_tight_,
}

