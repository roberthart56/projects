# ESP 32

Here are MAC addresses of the three boards I'm using now:
1:  34:85:18:24:EB:74  {0x34,0x85,0x18,0x24,0xEB,0x74}
2:  34:85:18:04:05:FC  {0x34,0x85,0x18,0x04,0x05,0xFC}
3:  34:85:18:03:C0:BC  {0x34, 0x85, 0x18, 0x03, 0xC0, 0xBC}

1/8/23  Got one esp32 to send pot reading to another!

Problems with bootloader?  Maybe solved by using manual boot mode.  See this link: 

https://learn.adafruit.com/adafruit-qt-py-esp32-c3-wifi-dev-board/arduino-neopixel-blink 

Also worked with Bobby at Harvard, found in xiao wiki the claim that pulling down pins x x x.....

On the receive end, use the callback function to serial print the received byte.
Can also send float by converting to array of bytes and reconverting at the receive end.

1/10/24
Installed Micropython on ESP32 xiao.


https://wiki.seeedstudio.com/XIAO_ESP32C3_MicroPython/

Clone esptool to a directory:
git clone https://github.com/espressif/esptool.git

Download the latest firmware.
https://micropython.org/download/esp32c3/

Navigate to the esptool folder in the esptool downloaded folder, put the firmware binary in that folder.

Flash the firmware:python  esptool.py --chip esp32c3 --port COM21 --baud 921600 --before default_reset --after hard_reset --no-stub  write_flash --flash_mode dio --flash_freq 80m 0x0 ESP32_GENERIC_C3-20240105-v1.22.1.bin

This erases and flashes device on COM18 with firmware in file downloaded from micropython site:


This works still, 2/21/24.  Could not flash one that was attached to an LED, drawing ~few mA from 3.3V and into at least one GPIO pin.  OK when I detached and floated all inputs in space.


1/11/24

Look at ESPNow examples in micropython.

A Set of utilities and functions for simplifying and making more robust:  https://github.com/glenn20/micropython-espnow-utils

And this:  https://github.com/orgs/micropython/discussions/11110

Micropython reference with a very simple example:  https://docs.micropython.org/en/latest/library/espnow.html


1/12/24

Used very simple example linked above, which worked as given.  Very nice workflow with Thonny editor modifying files on the esp32 directly, Arduino as a serial monitor. This is much easier than compiling in Arduino IDE.  Python code is very readable.  See simple send/receive files here.  My only confusion is the format of the byte array, and how it ends up being printed by the receiving esp32.  