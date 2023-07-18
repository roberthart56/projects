from machine import Pin, PWM, ADC
import time

mag_sensor = 40000
motor_pwm = 10000


adc = ADC(Pin(29))  # create ADC object on ADC pin
pwm0 = PWM(Pin(26))  # create PWM object from a pin
pwm0.freq(1000)  # set frequency
pwm0.duty_u16(motor_pwm)  # set duty cycle, range 0-65535

# while adc.read_u16() < 24000:
#     time.sleep(0.001)
    


while True:
   print(adc.read_u16())
   time.sleep(0.010)
