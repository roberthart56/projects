import machine
import time


p7 = machine.Pin(7)
pwm7 = machine.PWM(p7)
adc_r = machine.ADC(3)
adc_h = machine.ADC(2)            # create ADC object on ADC pin

adc_r.atten(machine.ADC.ATTN_11DB)       #Full range: 3.3v
adc_r.width(machine.ADC.WIDTH_12BIT) 		
adc_h.atten(machine.ADC.ATTN_11DB)       #Full range: 3.3v
adc_h.width(machine.ADC.WIDTH_12BIT) 		


pwm7.freq(100)
pwm7.duty(512)		#full range 1023

setpoint=2000
max_time = 120000
t1=time.ticks_ms()
while True:
    home=adc_h.read()
    remote=adc_r.read()
    setpoint = 3200 - remote
    print(home, ',', remote, ',', setpoint)			
    if (home < setpoint):
        pwm7.duty(min((setpoint - home)*10, 500))
    else:
        pwm7.duty(0)
    time.sleep(0.05)
    t2=time.ticks_ms()
    if time.ticks_diff(t2, t1) > max_time:
        break


