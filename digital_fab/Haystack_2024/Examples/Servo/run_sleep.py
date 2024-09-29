from machine import Pin,PWM
from time import sleep_us

signal = Pin(2, mode=Pin.OUT)

on_time = 500 #0.5 milliseconds min, 2.4 ms max.
off_time = 20000 - on_time

while True:
    signal.on()
    sleep_us(on_time)
    signal.off()
    sleep_us(off_time)



# 0.5ms/20ms = 0.025 = 2.5% duty cycle
# 2.4ms/20ms = 0.12 = 12% duty cycle

# 0.025*65535=1638
# 0.12*65535=7864

# while True:
#     sg90.duty_u16(1638)
#     sleep(1)
#     sg90.duty_u16(7864)
#     sleep(1)
