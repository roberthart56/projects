
import machine
from neopixel import NeoPixel
from time import sleep

Num_pix = 192

pixels1 = NeoPixel(machine.Pin(20), Num_pix)  #set up Pixel array
pixels2 = NeoPixel(machine.Pin(21), Num_pix)  #set up Pixel array

adc = machine.ADC(2)            # create ADC object on ADC pin
adc.atten(machine.ADC.ATTN_11DB)       #Full range: about 2.7 V on the esp32.  Requires a series resistor before the pot to give full range in turning the pot.
adc.width(machine.ADC.WIDTH_12BIT) 		#report ADC read in range 0 - 4000


while True:
    d=adc.read()
    
    index = int(d/20.5)  #need an integer for index
    
    if index > Num_pix-1:  #keep index under the limit of number of pixels.
        index = Num_pix-1
    print(d,index)
    
    index1=index
    index2 = Num_pix - 1 - index
    
    pixels1[index1] = (100,0,0)  #maximum is 511
    pixels2[index2] = (100,0,0)  #maximum is 511
    pixels1.write()
    pixels2.write()
    sleep(0.1)
    pixels1[index1] = (0,0,0)    #set pixels to zero.
    pixels2[index2] = (0,0,0)


  
pixels.write()




