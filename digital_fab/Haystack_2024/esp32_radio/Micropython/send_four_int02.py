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

#Can define a class to do this!  
adc1 = machine.ADC(2)            # create ADC object on ADC pin
adc2 = machine.ADC(3)
adc3 = machine.ADC(4)
adc4 = machine.ADC(5)			# create ADC object on ADC pin

adc1.atten(machine.ADC.ATTN_11DB)       #Full range: about 2.7 V on the esp32.  Requires a series resistor before the pot to give full range in turning the pot.
adc1.width(machine.ADC.WIDTH_12BIT) 		#report ADC read in range 0 - 4000
adc2.atten(machine.ADC.ATTN_11DB)       #Full range: about 2.7 V on the esp32.  Requires a series resistor before the pot to give full range in turning the pot.
adc2.width(machine.ADC.WIDTH_12BIT) 		#report ADC read in range 0 - 4000
adc3.atten(machine.ADC.ATTN_11DB)       #Full range: about 2.7 V on the esp32.  Requires a series resistor before the pot to give full range in turning the pot.
adc3.width(machine.ADC.WIDTH_12BIT) 		#report ADC read in range 0 - 4000
adc4.atten(machine.ADC.ATTN_11DB)       #Full range: about 2.7 V on the esp32.  Requires a series resistor before the pot to give full range in turning the pot.
adc4.width(machine.ADC.WIDTH_12BIT) 		#report ADC read in range 0 - 4000

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
