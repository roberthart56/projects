from machine import Pin, PWM, ADC
import time

mag_sensor = 40000
motor_pwm = 10000
setpoint = 1480

adc = ADC(Pin(29))  # create ADC object on ADC pin
pwm0 = PWM(Pin(26))  # create PWM object from a pin
pwm0.freq(1000)  # set frequency
pwm0.duty_u16(motor_pwm)  # set duty cycle, range 0-65535

while adc.read_u16() < 24000:
    time.sleep(0.001)
    


while True:
    for setpoint in range(1480, 1500):		#run through a range of periods
        for _ in range(50):				#do xx cycles at each period.
        
            while adc.read_u16() > 16000:
                time.sleep(0.001)
            
            start = time.ticks_ms()
            
            while adc.read_u16() < 24000:
                time.sleep(0.001)
            
            while adc.read_u16() > 16000:
                time.sleep(0.001)
            
            diff = time.ticks_ms()-start
            print(diff, setpoint)
            
            correct = diff - setpoint
            
            motor_pwm = motor_pwm + correct
            pwm0.duty_u16(motor_pwm)
