import machine
import time

ledpin26 = machine.Pin(26, machine.Pin.OUT)

ledpin26.off()


while True:
  ledpin26.on()
  time.sleep(0.001)
  ledpin26.off()
  time.sleep(0.010)
  