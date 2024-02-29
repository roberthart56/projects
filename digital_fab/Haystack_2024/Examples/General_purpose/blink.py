import machine
import time

led = machine.Pin(7, machine.Pin.OUT)

while True:
    led.value(1)
    time.sleep(1.0)
    led.value(0)
    time.sleep(1.0)
