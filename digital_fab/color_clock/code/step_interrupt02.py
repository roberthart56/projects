#step_interrupt02.py
#2/20/26   modify to initialize timer outside of interrupt loop.
#remove variable to detect change in period.  Just increment step_duration
#modify pin numbers to reflect wiring of oled and buttons in case.

from machine import SoftI2C, Pin, PWM, Timer

from time import sleep

import ssd1306

from oled_numbers import draw_number

# ------- Global variables ------

counter = 0
step_duration = 1000   #milliseconds
step_inc = 10


# ----- Hardware Setup -----

pwma = PWM(Pin(27), freq=50000, duty_u16=32768)  # vref for A
pwmb = PWM(Pin(29), freq=50000, duty_u16=32768)   #vref for B
pwma.duty_u16(2150) #with .3 mOhm Sense Resistor, I = V/3
pwmb.duty_u16(2400)

button_plus = Pin(2, Pin.IN, Pin.PULL_UP)
button_minus = Pin(1, Pin.IN, Pin.PULL_UP)

A1_in = Pin(6, Pin.OUT)
A2_in = Pin(7, Pin.OUT)
B1_in = Pin(28, Pin.OUT)
B2_in = Pin(4, Pin.OUT)


# REF_A = Pin(27, Pin.OUT)	#for 30 Ohm phase and 5V supply, set current to max.
# REF_B = Pin(29, Pin.OUT)
# REF_A.on()
# REF_B.on()

i2c = SoftI2C(scl=Pin(3), sda=Pin(0))
display = ssd1306.SSD1306_I2C(128, 64, i2c)

motor_timer = Timer()

# ------ Functions ------

def interrupt_handler(timer):
    
    global counter
    step(counter)
    counter = (counter+1)%4
            
def timer_init(T):
    motor_timer.init(period=T, mode=Timer.PERIODIC, callback=interrupt_handler)


def stepper_off():
    
    A1_in.off()
    A2_in.off()
    B1_in.off()
    B2_in.off()

def step(n):
    
    if n == 0:
        A1_in.on()
        A2_in.off()
        B1_in.on()
        B2_in.off()
    
    elif n == 1:
        A1_in.on()
        A2_in.off()
        B1_in.off()
        B2_in.on()
        
    elif n == 2:
        A1_in.off()
        A2_in.on()
        B1_in.off()
        B2_in.on()
        
    else:
        A1_in.off()
        A2_in.on()
        B1_in.on()
        B2_in.off()



def main():
    
    global step_duration
    print(step_duration)
    timer_init(step_duration)
    
    
#     print(step_duration)
    draw_number(display, step_duration)   #passing the oled object as a function argument
    
#     display.fill(0)  # Clear the screen
#     display.text(str(step_duration), 10, 25)
#     display.show()  # Show the text
    
    while True:
        
        if not button_plus.value():
            step_duration += step_inc
            timer_init(step_duration)
            sleep(0.25)
            draw_number(display, step_duration)   #passing the oled object as a function argument
#             print(step_duration)
#             display.fill(0)  # Clear the screen
#             display.text(str(step_duration), 10, 25)
#             display.show()  # Show the text
     
        if not button_minus.value():
            step_duration -= step_inc
            timer_init(step_duration)
            sleep(0.25)
            draw_number(display, step_duration)   #passing the oled object as a function argument
#             print(step_duration)
#             display.fill(0)  # Clear the screen
#             display.text(str(step_duration), 10, 25)
#             display.show()  # Show the text
#      
            
    
    
if __name__ == "__main__":

    main()


