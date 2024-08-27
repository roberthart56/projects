import random

def random_four_byte_write_new() -> bytearray:
    randy = bytearray(4)
    for i in range(4):
        randy[i] = random.randint(0, 254)

    return randy


def random_four_byte_check_match(a: bytes, b: bytearray) -> bool:
    for i in range(4):
        if a[i] != b[i]:
            return False 
        
    return True 


def random_five_alpha_character_gen() -> str:
    result = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(5))
    return result
