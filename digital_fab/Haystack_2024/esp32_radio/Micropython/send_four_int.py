import network
import espnow
import struct

# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.STA_IF)  # Or network.AP_IF
sta.active(True)
sta.disconnect()      # For ESP8266

e = espnow.ESPNow()
e.active(True)
#\x34\x85\x18\x24\xEB\x74 is dev. 1.
peer = b'\x34\x85\x18\x03\xC0\xBC'   # MAC address of peer's wifi interface (No.3)
e.add_peer(peer)      # Must add_peer() before send()

for i in range(10):
    
    integers = (1000+i, 2000+i, 3000+i, 4000+i)

    # Pack the integers into a bytes object.
    data = struct.pack('4h', *integers)

    # Send the data to the receiver.
    e.send(peer, data)


#e.send(peer, byte_array, True) 
#e.send(peer, "Starting...")
#e.send(peer, str(12), True)
#e.send(peer, b'end')
