###################

 

import ssd1306

import framebuf

from machine import SoftI2C, Pin, freq

from ulab import numpy as np

import random

import time

 

 

def step(a):

    b = np.zeros(a.shape, dtype=np.uint8)

    b[:, :] = a

    # sum all neighbors

    b += np.roll(a, 1, axis=0) + np.roll(a, -1, axis=0)

    b += np.roll(a, 1, axis=1) + np.roll(a, -1, axis=1)

    b += np.roll(np.roll(a, 1, axis=0), 1, axis=1) + np.roll(np.roll(a, -1, axis=0), 1, axis=1)

    b += np.roll(np.roll(a, 1, axis=0), -1, axis=1) + np.roll(np.roll(a, -1, axis=0), -1, axis=1)

    # logical operator encoding the rules

    return (b == 3) | (a & (b==4))

 

 

def main():

    freq(250000000)

 

    i2c = SoftI2C(scl=Pin(7), sda=Pin(6))

    display = ssd1306.SSD1306_I2C(128, 64, i2c)

 

    width = 128

    height = 64

   

    a = np.zeros((height, width), dtype=np.bool)

   

    # random initialization

    for i in range(height):

        for j in range(width):

            a[i, j] = random.getrandbits(1)

 

    i = 0

    while True:

        t1 = time.ticks_ms()

        display.fill(0)

        fb = framebuf.FrameBuffer(a.tobytes(), width, height, framebuf.GS8)

        display.blit(fb, 0, 0)

        display.show()

        a = step(a)

        t2 = time.ticks_ms()

        i += 1

        if i == 10:

            print(f"dt: {time.ticks_diff(t2, t1)} ms")

            i = 0

 

 

if __name__ == "__main__":

    main()

 

###################