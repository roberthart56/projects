

'''
rec_four_int_pixel03.py   3/22/24

receives four integers controls
position and color on pixel strip.

position: as sent, expect (0-Num_pix)
color: as sent, expect (0-255)

'''

import network
import espnow
import struct
from neopixel import NeoPixel
import machine

Num_pix = 200  # expect 0 - 190
pixels = NeoPixel(machine.Pin(10), Num_pix)

# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.STA_IF)
sta.active(True)
#sta.disconnect()   # Because ESP8266 auto-connects to last Access Point

e = espnow.ESPNow()
e.active(True)
     
while True:
    host, msg = e.recv(5)  #5 msec timeout
    if msg:             # msg == None if timeout in recv()
        #print(host, msg)
        if msg == b'end':
            break
        integers = struct.unpack('4h', msg)
        #print('Received integers:', integers)
        (a,b,c,d) = integers
        if a > Num_pix-1:
            a = Num_pix-1
        pixels[a] = (b,c,d)
        pixels.write()
        


