
'''
rec_four_int01.py   3/22/24

receives four integers and maps them to
position and color on pixel strip.

'''

import network
import espnow
import struct
from neopixel import NeoPixel
import machine

Num_pix = 5

pixels1 = NeoPixel(machine.Pin(10), Num_pix)

# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.STA_IF)
sta.active(True)
#sta.disconnect()   # Because ESP8266 auto-connects to last Access Point

e = espnow.ESPNow()
e.active(True)

def color_map(p1,p2,p3):
    r = int(p1/10)
    g = int(p2/10)
    b = int(p3/10)
    return(r,g,b)
    
def light_pix(arr):
     (a,b,c,d) = arr
     position = int(a/1000)
     
     if position > Num_pix:
         position = Num_pix
     pixels1[position] = color_map(b,c,d)
     pixels1.write()
     
while True:
    host, msg = e.recv(5)  #5 msec timeout
    if msg:             # msg == None if timeout in recv()
        #print(host, msg)
        if msg == b'end':
            break
        integers = struct.unpack('4h', msg)
        print('Received integers:', integers)
        light_pix(integers)
        

