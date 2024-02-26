from machine import Pin,PWM
import time 

buzz = PWM(Pin(2, mode=Pin.OUT))
buzz.freq(1000000)
# buzz.duty(512)

# for _ in range(1000):
#     for i in range(500):
#         buzz.duty(i)
 
half_period = 2000

for _ in range(1000):
    t1=time.ticks_us()

    buzz.duty(500)
    while time.ticks_diff(time.ticks_us(), t1) < half_period:
        pass

    buzz.duty(0)
    while time.ticks_diff(time.ticks_us(), t1) < 2*half_period:
        pass
    