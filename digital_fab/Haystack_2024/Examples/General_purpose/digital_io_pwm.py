from machine import Pin, PWM
import time

buzz = PWM(Pin(0))
buzz.freq(1000)

p1 = Pin(1, Pin.IN, machine.Pin.PULL_UP)  #input pin with pullup.

#print(p1.value())

while True:
    if p1.value():
        buzz.duty_u16(0)	#value in range 0 - 65k	
    else:
        buzz.duty_u16(3000)
        
    
#     time.sleep(0.1)



# while True:
#     led.value(1)
#     time.sleep(1.0)
#     led.value(0)
#     time.sleep(1.0)