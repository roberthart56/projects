### Byte Order Prefix

- `<`: Specifies little-endian byte order. This means that the least significant byte is stored first.

### Format Characters

- `b: int8_t`, signed byte
- `B: uint8_t`, unsigned byte
- `h: int16_t`, signed short (2 bytes)
- `H: uint16_t`, unsigned short (2 bytes)
- `i or l: int32_t`, signed int/long (4 bytes). Generally, 'i' is used for int and 'l' for long, but they are often the same size in C on many platforms.
- `I or L: uint32_t`, unsigned int/long (4 bytes). As with 'i' and 'l', the choice between 'I' and 'L' depends on the specific use case.
- `q: int64_t`, signed long long (8 bytes)
- `Q: uint64_t`, unsigned long long (8 bytes)
- `f: float`, single precision floating point (4 bytes)
- `d: double`, double precision floating point (8 bytes)

### Logic 

- Lowercase letters (`b`, `h`, `i`, etc.) are used for signed types.
- Uppercase letters (`B`, `H`, `I`, etc.) are used for unsigned types.
- The size and precision increase as you move through the alphabet: `b` and `B` are 1 byte, `h` and `H` are 2 bytes, `i`, `I`, `l`, and `L` are 4 bytes, and so on.
- `f` and `d` stand for floating-point numbers, with `f` representing the smaller (single precision) and `d` the larger (double precision).