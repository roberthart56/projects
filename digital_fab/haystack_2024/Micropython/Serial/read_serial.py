import serial
import time

serial_port = 'COM7'
baud_rate = 115200  # Adjust as per your microcontroller's configuration
#print('step 1')

ser = serial.Serial(serial_port, baud_rate)
ser.flush()

#time.sleep(1.5)

while True:
    if ser.in_waiting>0:
        a=ser.readline()
        print(a)
        if a == b'7 on\r\n':
            print('turn on 7!')
    time.sleep(0.1)
