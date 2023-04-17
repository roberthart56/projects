import machine
from machine import Pin, PWM
import utime
import ustruct
import sys

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

###############################################################################
# Settings
adc = machine.ADC(machine.Pin(26))  # create ADC object on ADC pin

pwm0 = PWM(Pin(27))  # create PWM object from a pin
pwm_freq = 4920
pwm0.freq(pwm_freq)  # set frequency.   f/32/200 is cycles per second
pwm0.duty_u16(6000)



# Assign chip select (CS) pin (and start it high)
cs = machine.Pin(1, machine.Pin.OUT)

# Initialize SPI.  Follow pinout for xiao RP2040.  Exposed pins are as follows and use SPI0.
spi = machine.SPI(0,
                  baudrate=1000000,
                  polarity=1,
                  phase=1,
                  bits=8,
                  firstbit=machine.SPI.MSB,
                  sck=machine.Pin(2),
                  mosi=machine.Pin(3),
                  miso=machine.Pin(4))


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
utime.sleep(2.0)

# Run forever
for j in range(11):
    
    for i in range(5):
        utime.sleep(60)  #wait minute * i
        print(i)
    
    
    #Open file
    filename = "data"+str(j)+".txt"
    file=open(filename,"w")	# creation and opening of a CSV file in Write mode
    file.write(str(pwm_freq)  + "\n")	# Writing frequency data in the opened file
            
    for i in range(300):  #now take data
        # Read X, Y, and Z values from registers (16 bits each)
        data = reg_read(spi, cs, REG_DATAX0, 6)

        # Convert 2 bytes (little-endian) into 16-bit integer (signed)
        acc_x = ustruct.unpack_from("<h", data, 0)[0]
        acc_y = ustruct.unpack_from("<h", data, 2)[0]
        acc_z = ustruct.unpack_from("<h", data, 4)[0]
        
        #read magnetometer voltage
        
        value = adc.read_u16()
    #     print(acc_y)
    #     print(value)
        
        file.write(str(i+1) + "," + str(value) + "," + str(acc_y) + "\n")	# Writing data in the opened file
        utime.sleep(0.01)
        
    file.close()
    
     #increment frequency
    pwm_freq += 20
    pwm0.freq(pwm_freq)  # set frequency.   f/32/200 is cycles per second
