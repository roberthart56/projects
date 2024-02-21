from machine import Pin,PWM
import time 


buzz = PWM(Pin(2, mode=Pin.OUT))
buzz.freq(1000000)

wave01 = [0]*100
for i in range(50):
    wave01[i] = 500			#wave01 is a 100 point square wave. sample every 50 microseconds for 200 Hz
    
wave02 = [0]*100
for i in range(25):
    wave02[i] = 500			#wave02 is a 100 point square wave. sample every 50 microseconds for 400 Hz
for i in range(50,75):
    wave02[i] = 500	     
 

while True:
    for i in range(100):
        t1=time.ticks_us()
        duty_cycle = wave01[i]+wave02[i]
        buzz.duty(duty_cycle)
        while time.ticks_diff(time.ticks_us(), t1) < 40:			#wait until 50 usec 
            pass

    