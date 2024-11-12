
from machine import Pin
from neopixel import NeoPixel
import time

def rotate(l, n):
    return l[n:] + l[:n]

def populate(pix,arr):
    for i in range(numpix):
        pix[i] = arr[i]
        
numpix = 100

pixels = NeoPixel(Pin(10), numpix)

for i in range(numpix):
    pixels[i] = (0,0,0)
    

pixels.write()

time.sleep(1)

numpix = 95
a=[0]*numpix

pixels = NeoPixel(Pin(10), numpix)

for i in range(numpix):
    a[i] = (255, int(255*i/numpix), 0)
    pixels[i] = a[i]

pixels.write()        

# for _ in range(0):  #while True:
#     a=rotate(a,1)
#     for i in range(numpix):
#         pixels[i] = a[i]
#     pixels.write()
#     time.sleep(0.5)
# # for _ in range(3):
# 

        
# while True:
#     for j in range(1000):
#         for i in range(numpix):
#             pixels[i] = (255-i+j, i+j, 127 +i-j)
#         pixels.write()
#         time.sleep(0.02)
# 



