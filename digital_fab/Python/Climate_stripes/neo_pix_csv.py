
from machine import Pin
from neopixel import NeoPixel
import time

numpix = 95

pixels = NeoPixel(Pin(10), numpix)

csv_data = []


with open('tr_data.csv', 'r') as file:
    
    for line in file:
        
        row = float( line.strip())
        
        csv_data.append(row)

def color(a):				#defines color map
    r = (40 * a) if (a > 0) else 0
    g = 0
    b = (-100 * a + 100) if (a < 1) else 0
    return(int(r), int(g), int(b))


for i in range(0,numpix):
    pixels[i] = color(csv_data[i+5])

pixels.write()        

