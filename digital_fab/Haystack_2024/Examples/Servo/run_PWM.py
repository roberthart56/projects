from machine import Pin,PWM
from time import sleep

signal = PWM(Pin(2, mode=Pin.OUT))
signal.freq(50)

# 0.5ms/20ms = 0.025 = 2.5% duty cycle
# 2.4ms/20ms = 0.12 = 12% duty cycle

# 0.025*65535=1638
# 0.12*65535=7864

while True:
    signal.duty_u16(2000)
    sleep(1)
    signal.duty_u16(7000)
    sleep(1)