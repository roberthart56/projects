from machine import Pin,PWM
import time 
import math

buzz = PWM(Pin(2, mode=Pin.OUT))
buzz.freq(1000000)

wave01 = [0]*100
for i in range(100):
    wave01[i] = math.sin(i*2*math.pi/50)
 

while True:
    for i in range(100):
        t1=time.ticks_us()
        duty_cycle = int(500*(1+wave01[i]))
        buzz.duty(duty_cycle)
        while time.ticks_diff(time.ticks_us(), t1) < 50:			#wait until 50 usec 
            pass

    