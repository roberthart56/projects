from machine import Pin, PWM, ADC
import time

mag_sensor = 40000
motor_pwm = 8000
setpoint = 1500

adc = ADC(Pin(29))  # create ADC object on ADC pin
pwm0 = PWM(Pin(26))  # create PWM object from a pin
pwm0.freq(1000)  # set frequency
pwm0.duty_u16(motor_pwm)  # set duty cycle, range 0-65535



while True:
    start = time.ticks_ms()
    value = adc.read_u16()  # read value, 0-65535 across voltage range 0.0v - 3.3v
    print(value)
#     
    time.sleep_ms(20)