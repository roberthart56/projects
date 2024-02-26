import machine
import time

adc = machine.ADC(2)            # create ADC object on ADC pin
adc.atten(machine.ADC.ATTN_11DB)       #Full range: 3.3v
adc.width(machine.ADC.WIDTH_12BIT) 					
for _ in range(100):
    d=adc.read()  # read a raw analog value in the range 0-65535       
    print(d)			
    time.sleep(0.5)