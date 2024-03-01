
from machine import Pin
from neopixel import NeoPixel

pixels = NeoPixel(Pin(20), 4)

    
pixels[0] = (0,125,0)
pixels[1] = (125,0,0)
pixels[2] = (0,0,125)
pixels[3] = (125,125,125)
  
pixels.write()


