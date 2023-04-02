from machine import Pin, PWM
import time

step = Pin(1, Pin.OUT, value=0)



pwm0 = PWM(Pin(1))  # create PWM object from a pin
pwm0.freq(4000)  # set frequency
pwm0.duty_u16(6000)

while True:
    pass