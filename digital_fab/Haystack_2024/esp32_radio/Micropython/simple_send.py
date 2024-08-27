import network
import espnow

# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.STA_IF)  # Or network.AP_IF
sta.active(True)
sta.disconnect()      # For ESP8266

e = espnow.ESPNow()
e.active(True)
#\x34\x85\x18\x24\xEB\x74 is dev. 1.
peer = b'\x34\x85\x18\x03\xC0\xBC'   # MAC address of peer's wifi interface (No.3)
e.add_peer(peer)      # Must add_peer() before send()

e.send(peer, "Starting...")
for i in range(10):
    e.send(peer, str(i), True)
e.send(peer, b'end')