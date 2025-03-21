from machine import Pin, PWM, ADC
import time

mag_sensor = 40000
motor_pwm = 18000
setpoint = 1500

adc = ADC(Pin(28))  # create ADC object on ADC pin
pwm0 = PWM(Pin(26))  # create PWM object from a pin
pwm0.freq(1000)  # set frequency
pwm0.duty_u16(motor_pwm)  # set duty cycle, range 0-65535




while True:
   print( adc.read_u16())
   time.sleep(0.5)
   