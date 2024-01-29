import network
import espnow
import time

# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.STA_IF)  # Or network.AP_IF
sta.active(True)
sta.disconnect()      # For ESP8266

my_sender = espnow.ESPNow()    #give this instance of ESPNow a name of your choice.
my_sender.active(True)
peer = b'\x34\x85\x18\x24\xEB\x74'  # (1) MAC address of peer's wifi interface
my_sender.add_peer(peer)      # Must add_peer() before send()

my_sender.send(peer, "Starting...")
for i in range(100):
    #e.send(peer, str(i), True)
    my_sender.send(peer, bytes([i]), True)  
    time.sleep(0.5)
my_sender.send(peer, b'end')