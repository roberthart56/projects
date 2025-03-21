from machine import Pin, PWM, ADC
import time

pin4 = Pin(4, Pin.OUT, value=0)
pin2 = Pin(2, Pin.OUT, value=0)


pwm = PWM(Pin(4))  # create PWM object from a pin
pwm.freq(50)  # set frequency
pwm.duty_u16(1650)

def pwm_set(pos):
 dc = int(pos*1650)+4950
 pwm.duty_u16(dc)

amp=1
period = 0.75

while True:
    start = time.ticks_ms()
    for x in range(-10,10):
        pwm_set(amp*x/10)
        time.sleep(period/40)
        #print(x)
    
    for x in range(10,-9, -1):
        pwm_set(amp*x/10)
        time.sleep(period/40)
        #print(x)
    pwm_set(-1)
    while (time.ticks_ms() - start) < period:
        pass
#     print(diff)
    