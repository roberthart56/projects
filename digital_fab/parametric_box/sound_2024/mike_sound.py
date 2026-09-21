import time
import machine

led1 = machine.Pin(3, machine.Pin.OUT)
led2 = machine.Pin(4, machine.Pin.OUT)

adc = machine.ADC(2)            # create ADC object on ADC pin
adc.atten(machine.ADC.ATTN_11DB)       #Full range: 3.3v
adc.width(machine.ADC.WIDTH_12BIT) 					

while True:
    d1=adc.read()  # read a raw analog value in the range 0-65535       
#     time.sleep(0.001)
    d2=adc.read()
    time.sleep(0.02)
    d3=adc.read()
    diff_low = abs(d1-d3)
    diff_high = abs(d1-d2)
    #print(diff_low)			
    #time.sleep(0.01)
    if diff_low>200:
        led1.value(1)
    else:
        led1.value(0)
    
    print(diff_low, diff_high)
    
    if diff_high>50:
        led2.value(1)
    else:
        led2.value(0)