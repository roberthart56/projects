# Soft_SPI_adxl343_RGB.Jan24.py  runs software SPI on RP2040.
# See Eagle project for board that fits on the XIAO package.
#  Software SPI allows direct routing to pins.

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

#PWM pins for RGB
# r_led = Pin(6, Pin.OUT)
# r_led(0)
pwm_r = PWM(Pin(26))  # create PWM object from a pin
pwm_g = PWM(Pin(27))  # create PWM object from a pin
pwm_b = PWM(Pin(28))  # create PWM object from a pin
pwm_r.freq(1000)  # set frequency
pwm_g.freq(1000)  # set frequency
pwm_b.freq(1000)  # set frequency
#pwm_r.duty_u16(40000)  # set duty cycle, range 0-65535

# Assign chip select (CS) pin (and start it high)
cs = machine.Pin(3, machine.Pin.OUT)

# Initialize SPI.  Follow pinout for xiao RP2040.  Exposed pins are as follows and use SPI0.
spi = machine.SoftSPI(baudrate=100000,
                  polarity=1,
                  phase=1,
                  bits=8,
                  firstbit=machine.SPI.MSB,
                  sck=machine.Pin(1),
                  mosi=machine.Pin(2),
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
while True:
    # Read X, Y, and Z values from registers (16 bits each)
    data = reg_read(spi, cs, REG_DATAX0, 6)

    # Convert 2 bytes (little-endian) into 16-bit integer (signed)
    acc_x = ustruct.unpack_from("<h", data, 0)[0]
    acc_y = ustruct.unpack_from("<h", data, 2)[0]
    acc_z = ustruct.unpack_from("<h", data, 4)[0]

    acc_x = acc_x * SENSITIVITY_2G * EARTH_GRAVITY
    acc_y = acc_y * SENSITIVITY_2G * EARTH_GRAVITY
    acc_z = acc_z * SENSITIVITY_2G * EARTH_GRAVITY

    # Print results
    print("X:", "{:.2f}".format(acc_x), \
          "| Y:", "{:.2f}".format(acc_y), \
          "| Z:", "{:.2f}".format(acc_z))
    
    
    # Convert to PWM duty cycles
    duty_cycle_r = 65535 - int (abs(5000*acc_x))
    duty_cycle_g = 65535 - int (abs(5000*acc_y))
    duty_cycle_b = 65535 - int (abs(5000*acc_z))
    #print(acc_x)
    pwm_r.duty_u16(duty_cycle_r)  # set duty cycle, range 0-65535
    pwm_g.duty_u16(duty_cycle_g)  # set duty cycle, range 0-65535
    pwm_b.duty_u16(duty_cycle_b)  # set duty cycle, range 0-65535
    #print(pwm_r.duty_u16())
    # Convert measurements to [m/s^2]
    print(pwm_r.duty_u16())
    print(pwm_g.duty_u16())
    print(pwm_b.duty_u16())
    utime.sleep(0.1)