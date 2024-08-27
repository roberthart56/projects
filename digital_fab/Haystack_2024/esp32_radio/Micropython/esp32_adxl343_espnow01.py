'''
esp32_adxl343_espnow01.py

program to send raw accelerometer data through espNow.
as data for pixel strip with Num_pix pixels.

Position data is normalized to Num_pix.

'''


import machine
import utime
import sys
import network
import espnow
import struct


###############################################################################
# Constants

# Registers
REG_DEVID = 0x00
REG_POWER_CTL = 0x2D
REG_DATAX0 = 0x32


# Other constants
DEVID = 0xE5
SENSITIVITY_2G = 1.0 / 256  # (g/LSB)
EARTH_GRAVITY = 9.80665  # Earth's gravity in [m/s^2]
Num_pix = 200
###############################################################################
# Settings

# Assign chip select (CS) pin (and start it high)
cs = machine.Pin(20, machine.Pin.OUT)

# Initialize SPI.  Follow pinout for esp32c3.  Exposed pins are as follows and use SPI0.
spi = machine.SPI(1,
                  baudrate=1000000,
                  polarity=1,
                  phase=1,
                  bits=8,
                  firstbit=machine.SPI.MSB,
                  sck=machine.Pin(8),
                  mosi=machine.Pin(10),
                  miso=machine.Pin(9))

# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.STA_IF)  # Or network.AP_IF
sta.active(True)
sta.disconnect()      # For ESP8266

e = espnow.ESPNow()
e.active(True)
#\x34\x85\x18\x24\xEB\x74 is dev. 1.
peer = b'\x34\x85\x18\x03\xC0\xBC'   # MAC address of peer's wifi interface (No.3)
e.add_peer(peer)      # Must add_peer() before send()
###############################################################################
# Functions



def reg_write(spi, cs, reg, data):
    """
    Write 1 byte to the specified register.
    """

    # Construct message (set ~W bit low, MB bit low)
    msg = bytearray()
    msg.append(0x00 | reg)
    msg.append(data)

    # Send out SPI message
    cs.value(0)
    spi.write(msg)
    cs.value(1)


def reg_read(spi, cs, reg, nbytes=1):
    """
    Read byte(s) from specified register. If nbytes > 1, read from consecutive
    registers.
    """

    # Determine if multiple byte (MB) bit should be set
    if nbytes < 1:
        return bytearray()
    elif nbytes == 1:
        mb = 0
    else:
        mb = 1

    # Construct message (set ~W bit high)
    msg = bytearray()
    msg.append(0x80 | (mb << 6) | reg)

    # Send out SPI message and read
    cs.value(0)
    spi.write(msg)
    data = spi.read(nbytes)
    cs.value(1)

    return data


###############################################################################
# Main

# Start CS pin high
cs.value(1)

# Workaround: perform throw-away read to make SCK idle high
reg_read(spi, cs, REG_DEVID)

# Read device ID to make sure that we can communicate with the ADXL343
data = reg_read(spi, cs, REG_DEVID)
if (data != bytearray((DEVID,))):
    print("ERROR: Could not communicate with ADXL343")
    sys.exit()

# Read Power Control register
data = reg_read(spi, cs, REG_POWER_CTL)
print(data)

# Tell ADXL343 to start taking measurements by setting Measure bit to high
data = int.from_bytes(data, "big") | (1 << 3)
reg_write(spi, cs, REG_POWER_CTL, data)

# Test: read Power Control register back to make sure Measure bit was set
data = reg_read(spi, cs, REG_POWER_CTL)
print(data)

# Wait before taking measurements
utime.sleep(1)

# Run forever
while True:
    for i in range(Num_pix):# Read X, Y, and Z values from registers (16 bits each)
        data = reg_read(spi, cs, REG_DATAX0, 6)

        # Convert 2 bytes (little-endian) into 16-bit integer (signed)
        acc_x = struct.unpack_from("<h", data, 0)[0]
        acc_y = struct.unpack_from("<h", data, 2)[0]
        acc_z = struct.unpack_from("<h", data, 4)[0]
        pos = int(i*4200/Num_pix)
        integers = (pos, acc_x, acc_y, acc_z)
        data_to_send = struct.pack('4h', *integers) #the * operator converts the tuple of four into four separate arguments.
        e.send(peer, data_to_send)
        print(acc_x, acc_y, acc_z)
   
        utime.sleep(0.1)
