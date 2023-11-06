PROJECT=45.echo.interrupt_edited
SOURCES=$(PROJECT).c
MMCU=attiny45
F_CPU = 8000000

CFLAGS=-mmcu=$(MMCU) -Wall -Os -DF_CPU=$(F_CPU)

$(PROJECT).hex: $(PROJECT).out
	avr-objcopy -O ihex $(PROJECT).out $(PROJECT).c.hex;\
	avr-size --mcu=$(MMCU) --format=avr $(PROJECT).out

$(PROJECT).out: $(SOURCES)
	avr-gcc $(CFLAGS) -I./ -o $(PROJECT).out $(SOURCES)


program-usbtiny: $(PROJECT).hex
	avrdude -p t45 -P usb -c usbtiny -U flash:w:$(PROJECT).c.hex
