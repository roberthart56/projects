# Programming the ATSAM and new ATTINY microcontrollers

We (i.e. Neil and his students) introduced two families of microcontroller starting in the Fall of 2019, and used them in Fab Academy in Spring 2020 and HTMAA Fall 2020.  Programming is now easier and cheaper in many ways, and the new microcontrollers are impressive.

**"Mega"Tiny family:** 
 * These are the successors of the attiny chips (tiny45 and 44), with built-in hardware communication, faster clocks, and more flexible pin use.   They can be programmed using the Arduino IDE.  Their pinouts are [here](https://github.com/SpenceKonde/megaTinyCore) on the Github documentation for the"Megatiny" Arduino Core by Konde.
 * Program with UPDI, uses pyUPDI through an FTDI interface.  Load hex file generated fromArduino core and toolchain using pyUPDI.  Success with Ubuntu and Raspberry PI 2B.  I have not succeeded on the MacOS, but itshould be possible.
 * Program with a UPDI programmer made from an "Arduino" board. Requires only a 328-based board.  All done through Arduino IDE, no FTDI needed.  Easiest.  I've done this on Windows, MacOS, Ubuntu, and  Raspberry Pi 2B with Arduino installed.  
 
 
 **ATSAMs:**
  * Describe and link to datasheets and pinouts and Arduino cores.
  * Bootloaders.
  * Programming with MAX32625PICO and pyOCD.
  
  ## Details
   1. Arduino Programmer:
    1. [instructions]((https://github.com/SpenceKonde/megaTinyCore/blob/master/MakeUPDIProgrammer.md)
    1. [Comments on proper choiceofUPDI programming resistor:](https://github.com/SpenceKonde/AVR-Guidance/blob/master/HardwareNotes/UPDISeriesResistors.md)  
