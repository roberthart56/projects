# MicroPython-RP2040



## Getting started

Notes on Micropython for RP2040.

Using xiao board.

Using PyCharm Micropython plugin. [Instructions here.](https://themachineshop.uk/getting-started-with-the-pi-pico-and-pycharm/) This works well.

[Quick reference for R2040 on Micropython site.](https://docs.micropython.org/en/latest/rp2/quickref.html#:~:text=RP2040%20has%20five%20ADC%20channels,range%20is%200%2D3.3V.)

Nice examples for output, PWM, and ADC.

SPI in MicroPython for adxl343 [from Digikey](https://www.digikey.be/en/maker/projects/raspberry-pi-pico-rp2040-spi-example-with-micropython-and-cc/9706ea0cf3784ee98e35ff49188ee045)

Pins on the adxl343 correspont to pins on the RP2040:
SCL = SCK P2, clock
SDA = MOSI P3, master TX
SDO = MISO P4, (Slave data out) Master RX
CS = Chip Select.  P1

This works, using alternate SPI0 pins.  Note that for each of two hardware SPI, there are three pin configs.

For representation of acceleration, check [adxl343 datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/adxl343.pdf)

According to the datasheet protocol, a read is done by 
 - CS low
 - Send register address, with bit 7 high for read, bit 6 optionally high for multiple bytes.
 - Read n bytes.
 - CS high.  (deassert).

In this program, data is read sequentially from six registers, using the SPI.read(n) function.  The sequential register reading is described on p13 of the adxl343 datasheet.  It requires setting the sixth bit of the register address high:  "To read or write multiple bytes in a single transmission, the multiple-byte bit, located after the R/W bit in the first byte transfer
(MB in Figure 27 to Figure 29), must be set. After the register
addressing and the first byte of data, each subsequent set of clock
pulses (eight clock pulses) causes the ADXL343 to point to the next
register for a read or write. This shifting continues until the clock
pulses cease and CS is deasserted."

[For diagram of the sequential reading of registers to get the six bytes needed for x,y, and z:](https://www.analog.com/media/en/technical-documentation/application-notes/AN-1077.pdf)

### ADXL343 Software SPI

Software SPI implemented to allow more direct routing of traces.  
[Code is here](./code/Soft_SPI_axdl343_RGB.Jan25.py).  Eagle Project [files are in CAD directory.](./cad)


## 23K256 memory chip as an example of SPI

The 23K256 is a 32KByte memory device with a limited set of commands and registers.  Good exercise for doing SPI at a low-ish level, using the MicroPython machine functions and referring to eh chip's datasheet.

[Datasheet for 23K256:](https://ww1.microchip.com/downloads/en/DeviceDoc/22100F.pdf)

Set Polarity equal to zero for this chip.  This is the level of the idle clock.  See [SPI spec for MicroPython](https://docs.micropython.org/en/latest/library/machine.SPI.html)

[Here is a code that works](./code/SPI_23K256/SPI_23K256.py) to store and retrieve numbers from the 23K256.  All operations are written out.  Next step would be to put them in functions and create a library file for this chip. 

This is a nice example of a simple but non-trivial protocol for SPI. 



## Feb 2024.

Use esp32c3 for its ability to battery manage.  Change pins and spi to use hardware spi, because that's the board that was available. This works, but gives overflow at high acc values for the PWM duty cycle.  Need to work on this, but looks like it should be solvable.  Take to Haystack.  Hope to iterate with cheaper and more reproducible solution.

