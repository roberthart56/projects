### MIDI Readme

July 20, 2021.  Spent some time figuring out how to send MIDI from Mega2560.  Easy to generate MIDI messages, but to get to USB, need to either use a MID/USB converter as we do with the keyboards, or write code for a native-USB board.  A couple of libraries exist for that.  I used the Arduino [MIDIUSB library](https://github.com/arduino-libraries/MIDIUSB).
Documenting some Arduino code:
* Code for Arduino mega2560 that sends on/off on a single note: [midi_mega2560_simple.ino](./midi_mega2560_simple.ino)
* Code for Arduino mega2560 that connects to pedal switches and sends on/off midi signals for an arbitrary number of pedals: [MIDI_Mega.ino](./MIDI_Mega.ino)
* Code for a USB native board, like the Metro M0 from Adafruit: [MIDI_7_notes.ino](./MIDI_7_notes.ino).  This code plays notes using digital inputs.
* Code that acts as a bridge between UART on mega2560 and the USB MIDI of the Metro M0: [MIDI_bridge_1.ino](./MIDI_bridge_1.ino).  This code is run on the native USB board, and can act as a MIDI-USB converter, although not all the functionality may be there for all kinds of commands.
