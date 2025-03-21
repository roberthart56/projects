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

amp=1.0
period = 2
while True:
    start = time.ticks_ms()
    pwm_set(-amp)
    time.sleep(period/2)
    pwm_set(amp)
    time.sleep(period/2)
    