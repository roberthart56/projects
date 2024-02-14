import machine
import time

buzz = machine.PWM(machine.Pin(0, machine.Pin.OUT))
buzz.freq(500)
# led = machine.Pin(0, machine.Pin.OUT)
# create an input pin on pin #1, no pull up resistor
p1 = machine.Pin(1, machine.Pin.IN)
# read and print the pin value
print(p1.value())

while True:
    if p1.value():
        buzz.duty_u16(3200)
    else:
        buzz.duty_u16(0)
    #led.value(p1.value())
#     time.sleep(0.1)



# while True:
#     led.value(1)
#     time.sleep(1.0)
#     led.value(0)
#     time.sleep(1.0)