

'''
rec_four_int_pixel02.py   3/22/24

receives four integers and maps them to
position and color on pixel strip.

'''

import network
import espnow
import struct
from neopixel import NeoPixel
import machine

Num_pix = 200
max_adc = 4100
pixels1 = NeoPixel(machine.Pin(10), Num_pix)

# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.STA_IF)
sta.active(True)
#sta.disconnect()   # Because ESP8266 auto-connects to last Access Point

e = espnow.ESPNow()
e.active(True)

def color_map1(p1,p2,p3):   #color map for pots.
    r = int(p1*255/max_adc)
    g = int(p2*255/max_adc)
    b = int(p3*255/max_adc)
    return(r,g,b)

def color_map2(p1,p2,p3):  #color map for accelerometer
    r = int(abs(p1)*255/max_adc)
    g = int(abs(p2)*255/max_adc)
    b = int(abs(p3)*255/max_adc)
    return(r,g,b)
    
def light_pix(arr):
     (a,b,c,d) = arr
     position = int(Num_pix*a/max_adc)  #
     
     if position > Num_pix-1:
         position = Num_pix-1
     pixels1[position] = color_map2(b,c,d)
     print('r,g,b = ', color_map2(b,c,d))
     pixels1.write()
     
while True:
    host, msg = e.recv(5)  #5 msec timeout
    if msg:             # msg == None if timeout in recv()
        #print(host, msg)
        if msg == b'end':
            break
        integers = struct.unpack('4h', msg)
        #print('Received integers:', integers)
        light_pix(integers)
        

