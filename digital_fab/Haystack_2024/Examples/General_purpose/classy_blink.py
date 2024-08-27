from machine import Pin
import time

class Flasher:
    def __init__(self, pin, on_time, off_time):
        self.ledPin = Pin(pin, Pin.OUT)
        self.OnTime = on_time  #time in milliseconds
        self.OffTime = off_time
        self.ledState = 0  # Assume 0 is off and 1 is on for LED state
        self.ledPin.value(0) # Start with LED off.
        self.previousMillis = time.ticks_ms()

    def Update(self):
        currentMillis = time.ticks_ms()
        if self.ledState == 1 and (time.ticks_diff(currentMillis, self.previousMillis) >= self.OnTime):
            self.ledState = 0  # Turn it off
            self.previousMillis = currentMillis  # Remember the time
            self.ledPin.value(self.ledState)  # Update the actual LED
        elif self.ledState == 0 and (time.ticks_diff(currentMillis, self.previousMillis) >= self.OffTime):
            self.ledState = 1  # turn it on
            self.previousMillis = currentMillis  # Remember the time
            self.ledPin.value(self.ledState)  # Update the actual LED

# Example usage
led1 = Flasher(2, 300, 600)  # GPIO 2, adjust as needed
led2 = Flasher(3, 2, 5)  # GPIO 3, adjust as needed


while True:
    led1.Update()
    led2.Update()
    time.sleep(0.001)  # Add a short delay to reduce CPU usage


