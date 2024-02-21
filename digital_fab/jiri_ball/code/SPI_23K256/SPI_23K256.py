import machine
import time

###############################################################################
# Constants

#commands
READ = 0x03
WRITE = 0x02
READ_S_R = 0x05
WRITE_S_R = 0x01

# Bits to determine mode
SEQ_RW = 0x01 << 6		#B6 is 1
BYTE_RW = 0x00 << 6		#zeros		
PAGE_RW = 0x02 << 6		#B7 is 1

#address
ADDR_HIGH = 0x00
ADDR_LOW = 0x00

#content
value_stored = 254

########################################################

# Assign chip select (CS) pin
cs = machine.Pin(1, machine.Pin.OUT)
time.sleep(0.1)


# Initialize SPI.  Use SPI0 with pins 1,2,3,4.
spi = machine.SPI(0,
                  baudrate=1000000,
                  polarity=0,
                  phase=1,
                  bits=8,
                  firstbit=machine.SPI.MSB,
                  sck=machine.Pin(2),
                  mosi=machine.Pin(3),
                  miso=machine.Pin(4))


#write to status register to set mode.
cs.value(1)

msg = bytearray()
msg.append(WRITE_S_R)
msg.append(BYTE_RW)
#print(msg)
cs.value(0)
spi.write(msg)   
cs.value(1)


#read status register, to check mode.
msg = bytearray()
msg.append(READ_S_R)
cs.value(0)
spi.write(msg)   
data = spi.read(1)
cs.value(1)
print("mode=",data)

#form address
msg = bytearray([WRITE, ADDR_HIGH, ADDR_LOW])

#form writing array
val = bytearray([value_stored])
print("number stored =",val)

#Write to address
cs.value(0)
spi.write(msg)
spi.write(val)   
cs.value(1)

time.sleep(0.01)

#Read from address
msg = bytearray([READ, ADDR_HIGH, ADDR_LOW])
cs.value(0)
spi.write(msg)   #same address
data = spi.read(1)   
cs.value(1)
print('number read = ',data)