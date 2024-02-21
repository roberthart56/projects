from machine import Pin
import time

r_led = Pin(7, Pin.OUT)

interval = 0.5
while True:
    r_led(1)
    time.sleep(interval)
    r_led(0)
    time.sleep(interval)