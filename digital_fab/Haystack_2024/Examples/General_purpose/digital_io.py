from machine import Pin
import time

led = Pin(0, Pin.OUT)   # create an input pin on pin #1, no pull up resistor

button = Pin(1, Pin.IN, Pin.PULL_UP)



while True:
    led.value(not(button.value()))
    print(button.value())
    time.sleep(0.1)



