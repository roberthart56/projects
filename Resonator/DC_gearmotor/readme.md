## DC geared motor, late March, 2023.

[link to Onshape Document](https://cad.onshape.com/documents/810912a80812297ee3f6f31a/w/e5f7bf5c68aee5e6deaae8a5/e/c3fc9c7d9465c664c7398cd7)

Micropython file in the Files folder here.

Set up small gearmotor to drive oscillating mass for resonator (massy active device on spring). Magnet in rotating cam.  Board with Hall sensor, RP2040 Xiao, MOSFET to drive motor, ADXL343 accelerometer.  Software just runs motor with PWM, adjusting so that magnetic signal appears with desired period.

This works, but frequency stability is only a few parts per thousand.  Software will be simpler using servomotor and timing loop.

It is clear from this prototype that phase shift above and below resonance will be detectable and useful in tuning precisely.