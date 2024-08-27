'''
send_four_int02.py   3/22/24

reads four adc channels 
and sends four integers 0-4096.

'''

import network
import espnow
import struct
import machine
import time


# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.STA_IF)  # Or network.AP_IF
sta.active(True)
sta.disconnect()      # For ESP8266

e = espnow.ESPNow()
e.active(True)
#\x34\x85\x18\x24\xEB\x74 is dev. 1.
peer = b'\x34\x85\x18\x03\xC0\xBC'   # MAC address of peer's wifi interface (No.3)
e.add_peer(peer)      # Must add_peer() before send()

while True:
    d1=adc1.read()
    d2=adc2.read()
    d3=adc3.read()
    d4=adc4.read()
    print(d1)
    integers = (d1, d2, d3, d4)
    data = struct.pack('4h', *integers) #the * operator converts the tuple of four into four separate arguments.
    e.send(peer, data)
    time.sleep(0.02)

#e.send(peer, byte_array, True) 
#e.send(peer, "Starting...")
#e.send(peer, str(12), True)
#e.send(peer, b'end')

