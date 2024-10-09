import serial

from time import sleep

serial_port = 'COM18'

ser = serial.Serial(serial_port) 
ser.flush()



while True:				
    if ser.in_waiting>0:
        a=ser.readline()
        print(a.decode('utf-8'))
        
    sleep(0.1)


