
from machine import Pin
from neopixel import NeoPixel
import time

numpix = 192
pixels = NeoPixel(Pin(2), numpix)

# for i in range(numpix):
#      pixels[i] = (255, 0, 0)
# pixels.write()        
        
#
while True:
    for j in range(10000):
        for i in range(numpix):
            pixels[i] = (255-i+j, i+j, 127 - i+j)
        pixels.write()
        time.sleep(0.02)



