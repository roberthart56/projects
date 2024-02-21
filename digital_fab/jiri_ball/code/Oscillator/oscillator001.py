import machine
import time

ledpin26 = machine.Pin(26, machine.Pin.OUT)

ledpin26.off()

now1 = time.ticks_ms()

while time.ticks_diff(time.ticks_ms(), now1) < 500:
    time.sleep(01)

#time.sleep(0.50)
now2 = time.ticks_ms()

print(now2 - now1)

while True:
  ledpin26.on()
  time.sleep(0.001)
  ledpin26.off()
  time.sleep(0.008)
  