#from tutorial at: https://mpy-tut.zoic.org/tut/network.html
#see also network basics: https://docs.micropython.org/en/latest/esp8266/tutorial/network_basics.html
#
#


import network
w = network.WLAN()
w.active(True)

ap = 'Purple Cow 4'
password = 'indiana0623'

w.connect(ap,password)
print(w.ifconfig()	)	#should return a tuple of (IP address, netmask, gateway address, DNS address).

def http_get(url):
    import socket
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
    while True:
        data = s.recv(100)
        if data:
            print(str(data, 'utf8'), end='')
        else:
            break
    s.close()

    
#http_get('http://micropython.org/ks/test.html')
http_get('https://api.weather.gov/gridpoints/TOP/31,80/forecast')