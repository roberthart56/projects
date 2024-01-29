import network
import espnow

# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.disconnect()   # Because ESP8266 auto-connects to last Access Point

my_rcvr = espnow.ESPNow()   #give this instance of ESPNow a name of your choice.
my_rcvr.active(True)

while True:
    host, msg = my_rcvr.recv()
    if msg:             # msg == None if timeout in recv()
        #print(host, msg)
        #print(msg)		# msg is a byte array
        #print(msg.decode('utf-8')[1])
        byteorder = 'big'  # or 'little' depending on the byte order
        print(int.from_bytes(msg, byteorder))
        if msg == b'end':
            break