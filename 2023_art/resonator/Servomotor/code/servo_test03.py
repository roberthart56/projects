from machine import Pin, PWM, ADC
import time
import array

pin4 = Pin(27, Pin.OUT, value=0)
diff = 0


pwm = PWM(Pin(27))  # create PWM object from a pin
pwm.freq(50)  # set frequency
pwm.duty_u16(1650)

def pwm_set(pos):
 dc = int(pos*1650)+4950
 pwm.duty_u16(dc)
 
amp_array = array.array('f',[0,-0.25, -0.5,-0.75, -1.0,-0.75,-0.5,-0.25,0,0.25,0.5,0.75,1.0,0.75,0.5,0.25])
amp=0.7
period = 1450000

while True:
    start = time.ticks_us()
    for i in range(16):
        pwm_set(amp*amp_array[i])
        while diff < (i+1)*period/16:
            diff = time.ticks_us()-start
    
    diff=0
    