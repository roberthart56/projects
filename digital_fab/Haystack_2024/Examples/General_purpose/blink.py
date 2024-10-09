from machine import Pin 
import time

led = Pin(7, Pin.OUT)   #led is created as an instance of the class Pin

while True:
    led.value(1)
    time.sleep(1.0)
    led.value(0)
    time.sleep(1.0)
