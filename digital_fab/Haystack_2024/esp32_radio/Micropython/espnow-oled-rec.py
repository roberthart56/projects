import network
import espnow
from oled_functions import oled_display

# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.disconnect()   # Because ESP8266 auto-connects to last Access Point

my_rcvr = espnow.ESPNow()   #give this instance of ESPNow a name of your choice.
my_rcvr.active(True)

while True:
    host, msg = my_rcvr.recv()
    if msg:             # msg == None if timeout in recv()
        int_value = int.from_bytes(msg, 'big') 
        print(int_value)
        oled_display(int_value)
        if msg == b'end':
            break