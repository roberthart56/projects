from machine import Pin
from time import sleep
button = Pin(1, Pin.IN, Pin.PULL_UP)

while True:
    print(button.value())
    sleep(0.1)