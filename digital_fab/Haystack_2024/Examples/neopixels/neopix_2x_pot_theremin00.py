
import machine
from neopixel import NeoPixel
from time import sleep

Num_pix = 192

pixels1 = NeoPixel(machine.Pin(10), Num_pix)  #set up Pixel array
#pixels2 = NeoPixel(machine.Pin(21), Num_pix)  #set up Pixel array

adc1 = machine.ADC(2)            # create ADC object on ADC pin
adc2 = machine.ADC(3)            # create ADC object on ADC pin

adc1.atten(machine.ADC.ATTN_11DB)       #Full range: about 2.7 V on the esp32.  Requires a series resistor before the pot to give full range in turning the pot.
adc1.width(machine.ADC.WIDTH_12BIT) 		#report ADC read in range 0 - 4000
adc2.atten(machine.ADC.ATTN_11DB)       #Full range: about 2.7 V on the esp32.  Requires a series resistor before the pot to give full range in turning the pot.
adc2.width(machine.ADC.WIDTH_12BIT) 		#report ADC read in range 0 - 4000

def color_model(a):
    if a < 10:
        return(0,0,0)
    elif a > 490:
        return(0,510,0)
    else:
        return(511-a,0,a) 	#maximum is 511
    

while True:
    d1=adc1.read()
    d2=adc2.read()
    
    in1 = int(d1/20.5)  #need an integer between  0 to 190
    in2 = int(d2/7.7)  #need an integer between 0 and 500 
    
    if in1 > Num_pix-1:  #keep index under the limit of number of pixels.
        in1 = Num_pix-1
        
    pixels1[in1] = color_model(in2)  
    pixels1.write()
    print(in1,in2)
    sleep(0.01)
    



  







