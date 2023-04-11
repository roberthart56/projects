from machine import Pin, PWM
import time

#step = Pin(27, Pin.OUT, value=0)

pwm_freq = 5294

pwm0 = PWM(Pin(27))  # create PWM object from a pin
pwm0.freq(pwm_freq)  # set frequency f/32/200 is cycles per second
pwm0.duty_u16(6000)

while True:
    time.sleep(1.0)
    print(pwm_freq)
#     pwm_freq += 2
#     pwm0.freq(pwm_freq) 