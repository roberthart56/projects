#Code to run unipolar stepper motor with the ULN2003 driver module.
#Adapted from https://microcontrollerslab.com/28byj-48-stepper-motor-raspberry-pi-pico-micropython/
#Robert Hart 6/18/2024.


from machine import Pin
from time import sleep

#set up pins.  these are pin designations in Micropython for
#the pins that fit the signal pins of the motor driver module
IN1 = Pin(0,Pin.OUT)
IN2 = Pin(7,Pin.OUT)
IN3 = Pin(6,Pin.OUT)
IN4 = Pin(29,Pin.OUT)

pins = [IN1, IN2, IN3, IN4]

#Set up array of sequences for energizing signal pins.
sequence = [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]

while True:
    for step in sequence:      #to reverse, use: 'for step in reversed(sequence)'
        for i in range(len(pins)):
            pins[i].value(step[i])
        sleep(0.03)  # Delay after each step determines rate. For 1:16 gearing, this is about 1 RPM. .
