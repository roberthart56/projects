import machine
import time

ledpin = machine.Pin(0, machine.Pin.OUT)
buttonpin = machine.Pin(7, machine.Pin.IN)

ledpin.off()

now1 = time.ticks_ms()

while time.ticks_diff(time.ticks_ms(), now1) < 500:
    time.sleep(0.011)

#time.sleep(0.50)
now2 = time.ticks_ms()

print(now2 - now1)

while True:
  ledpin.on()
  time.sleep(1)
  ledpin.off()
  time.sleep(1)
  