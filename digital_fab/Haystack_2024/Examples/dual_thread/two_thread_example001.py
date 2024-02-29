"""
Using global variable for inter thread communication
multi thread example
"""

from time import sleep
import _thread


def core0_thread():
    global r,s
    while True:
        sleep(1)
        print(r)
        s += 2
        

def core1_thread():
    global r,s
    while True:
        sleep(0.5)
        r += 1
        print(s)



# Global variable to send signals between threads
r = 0
s=100

second_thread = _thread.start_new_thread(core1_thread, ())
core0_thread()