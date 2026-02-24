# from machine import Pin, SoftI2C
# import ssd1306
import time

# ---------- I2C Setup ----------

# i2c = SoftI2C(scl=Pin(7), sda=Pin(6))
# oled = ssd1306.SSD1306_I2C(128, 64, i2c)


# ---------- Large Digit Font (16x32) ----------
# Each digit is drawn using rectangles

def draw_digit(oled, digit, x, y):

    seg = {
        "a": (x+2,  y,    12, 3),
        "b": (x+13, y+2,   3, 13),
        "c": (x+13, y+17,  3, 13),
        "d": (x+2,  y+30, 12, 3),
        "e": (x,    y+17,  3, 13),
        "f": (x,    y+2,   3, 13),
        "g": (x+2,  y+15, 12, 3),
    }

    digits = {
        "0": "abcfed",
        "1": "bc",
        "2": "abged",
        "3": "abgcd",
        "4": "fgbc",
        "5": "afgcd",
        "6": "afgecd",
        "7": "abc",
        "8": "abcdefg",
        "9": "abfgcd",
    }

    for s in digits[str(digit)]:
        oled.fill_rect(*seg[s], 1)


def draw_number(oled, number):

    oled.fill(0)

    num_str = "{:06d}".format(number)

    start_x = 10   # center on screen
    y = 14

    for i, d in enumerate(num_str):
        draw_digit(oled, d, start_x + i*20, y)

    oled.show()


# ---------- Demo Counter ----------
count = 0

# while True:
#     draw_number(oled, count)
#     count += 1
#     time.sleep(0.2)