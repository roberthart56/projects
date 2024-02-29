import serial
import time

from pygame import mixer
from time import sleep

mixer.init()

sound0 = mixer.Sound('250Hz.wav')
sound1 = mixer.Sound('1kHz.wav')
sound2 = mixer.Sound('la.wav')
sound3 = mixer.Sound('di.wav')
sound4 = mixer.Sound('da.wav')

serial_port = 'COM14'        #'/dev/ttyACM0'   'COM10'
baud_rate = 115200  


ser = serial.Serial(serial_port, baud_rate)
ser.flush()



while True:				#currently a test of each case.  Needs a loop method.
    if ser.in_waiting>0:
        a=ser.readline()
        print(a)
        if a == b'0 on\r\n':
            print('turn on 0!')
            sound0.play()
        if a == b'0 off\r\n':
            print('turn off 0!')
            sound0.fadeout(200)
        if a == b'1 on\r\n':
            print('turn on 1!')
            sound1.play()
        if a == b'1 off\r\n':
            print('turn off 1!')
            sound1.fadeout(200)
        if a == b'2 on\r\n':
            print('turn on 2!')
            sound2.play()
        if a == b'2 off\r\n':
            print('turn off 2!')
            sound2.fadeout(200)
        if a == b'3 on\r\n':
            print('turn on 3!')
            sound3.play()
        if a == b'3 off\r\n':
            print('turn off 3!')
            sound3.fadeout(200)
        if a == b'4 on\r\n':
            print('turn on 4!')
            sound4.play()
        if a == b'4 off\r\n':
            print('turn off 4!')
            sound4.fadeout(200)
    #time.sleep(0.1)

