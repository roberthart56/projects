
#create a byte array.
#byte_array_1 = bytes([65, 66, 67, 68, 69])

#buffer = bytearray([0xff] * 128)  #32x32

# Get the nth bit from a byte
def get_bit(byte, n):
    return (byte >> n) & 1

# Set the nth bit in a byte
def set_bit(byte, n):
    return ((byte) | (1 << n))

# Clear the nth bit in a byte
def clear_bit(byte, n):
    return ((byte) & ~(1 << n))

def get_x_y(array,w,x,y):	#Each row is (w//8) bytes.
    byte_no = (w//8)*y + x//8
    bit_no = x % 8
    return get_bit(array[byte_no], 7-bit_no)  # large end of byte corresponds to smaller x!

def set_x_y(array,w,x,y):	#assuming 32x32.  Each row is four bytes.
    byte_no = (w//8)*y + x//8
    bit_no = x % 8
    array[byte_no] = set_bit(array[byte_no], 7-bit_no)
    return array	

def clear_x_y(array,w,x,y):	#assuming 32x32.  Each row is four bytes.
    byte_no = (w//8)*y + x//8
    bit_no = x % 8
    array[byte_no] = clear_bit(array[byte_no], 7-bit_no)
    return array


