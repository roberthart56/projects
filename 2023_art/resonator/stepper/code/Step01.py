from machine import Pin
import time

step_pin = Pin(1, Pin.OUT)

interval = 0.001
while True:
    step_pin(1)
    time.sleep(0.0001)
    step_pin(0)
    time.sleep(interval)