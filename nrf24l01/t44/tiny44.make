PROJECT=nRF_09
SOURCES=$(PROJECT).c
MMCU=attiny44
F_CPU = 8000000

CFLAGS=-mmcu=$(MMCU) -Wall -Os -DF_CPU=$(F_CPU)

$(PROJECT).hex: $(PROJECT).out
	avr-objcopy -O ihex $(PROJECT).out $(PROJECT).c.hex;\
	avr-size --mcu=$(MMCU) --format=avr $(PROJECT).out
 
$(PROJECT).out: $(SOURCES)
	avr-gcc $(CFLAGS) -I./ -o $(PROJECT).out $(SOURCES)
 

program-avrisp2: $(PROJECT).hex
	avrdude -p attiny45 -P usb -c avrisp2 -U flash:w:$(PROJECT).c.hex

program-avrisp2-fuses: $(PROJECT).hex
	avrdude -p atmega168 -P usb -c avrisp2 -U lfuse:w:0x62:m
	avrdude -p atmega168 -P usb -c avrisp2 -U hfuse:w:0xFF:m
	avrdude -p atmega168 -P usb -c avrisp2 -U efuse:w:0xDF:m

program-usbtiny: $(PROJECT).hex
	avrdude -p attiny44 -P usb -c usbtiny -U flash:w:$(PROJECT).c.hex

program-usbtiny-fuses: $(PROJECT).hex
	avrdude -p atmega168 -P usb -c usbtiny -U lfuse:w:0x62:m
	avrdude -p atmega168 -P usb -c usbtiny -U hfuse:w:0xFF:m
	avrdude -p atmega168 -P usb -c usbtiny -U efuse:w:0xDF:m
