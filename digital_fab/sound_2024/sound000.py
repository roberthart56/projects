import time
import machine

led1 = machine.Pin(3, machine.Pin.OUT)

adc = machine.ADC(2)            # create ADC object on ADC pin
adc.atten(machine.ADC.ATTN_11DB)       #Full range: 3.3v
adc.width(machine.ADC.WIDTH_12BIT) 					

while True:
    d=adc.read()  # read a raw analog value in the range 0-65535       
    print(d)			
    time.sleep(0.01)
    if d>200:
        led1.value(1)
    else:
        led1.value(0)
        
