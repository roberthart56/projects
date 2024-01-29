from machine import Pin,PWM
from time import sleep

sg90 = PWM(Pin(29, mode=Pin.OUT))
sg90.freq(50)

# 0.5ms/20ms = 0.025 = 2.5% duty cycle
# 2.4ms/20ms = 0.12 = 12% duty cycle

# 0.025*65535=1638
# 0.12*65535=7864

while True:
    sg90.duty_u16(1638)
    sleep(1)
    sg90.duty_u16(7864)
    sleep(1)