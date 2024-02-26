from machine import Pin, ADC

import time

def get_temp():   
    adc_pin = Pin(2)
    
    adc = ADC(adc_pin)
    adc.atten(ADC.ATTN_11DB)		#Max is 2.8V with 11dB Atten.
    analog_value = adc.read_u16()	#adc.read() for 12 bits.
    return analog_value

for _ in range(100):
    print(get_temp())
    time.sleep(0.5)