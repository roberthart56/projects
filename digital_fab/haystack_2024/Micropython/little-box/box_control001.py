import machine
import time


p7 = machine.Pin(7)
pwm7 = machine.PWM(p7)

adc = machine.ADC(2)            # create ADC object on ADC pin
adc.atten(machine.ADC.ATTN_11DB)       #Full range: 3.3v
adc.width(machine.ADC.WIDTH_12BIT) 		


pwm7.freq(500)
pwm7.duty(512)

setpoint=2000

t1=
for _ in range(100):
    d=adc.read()  # read a raw analog value in the range 0-65535       
    print(d)			
    if (d < setpoint):
        pwm7.duty(400)
    else:
        pwm7.duty(0)
    time.sleep(0.5)


