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

def light_pix(arr):
     (a,b,c,d) = arr
     position = int(a/4)
     pixels1[position] = (b,c,d)
     pixels1.write()
     
while True:
    host, msg = e.recv(5)
    if msg:             # msg == None if timeout in recv()
        #print(host, msg)
        if msg == b'end':
            break
        integers = struct.unpack('4h', msg)
        print('Received integers:', integers)
        light_pix(integers)
        

