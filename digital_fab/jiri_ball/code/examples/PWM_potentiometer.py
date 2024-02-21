from machine import Pin, PWM, ADC
import time

pin6 = Pin(6, Pin.OUT, value=0)
pin7 = Pin(7, Pin.OUT, value=0)

adc = ADC(Pin(26))  # create ADC object on ADC pin
pwm0 = PWM(Pin(0))  # create PWM object from a pin
pwm0.freq(1000)  # set frequency


while True:
    value = adc.read_u16()  # read value, 0-65535 across voltage range 0.0v - 3.3v
    print(value)
    pwm0.duty_u16(value)  # set duty cycle, range 0-65535
    time.sleep_ms(100)