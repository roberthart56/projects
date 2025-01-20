
#scan_matrix_play_61 notes
#columns are attached to outputs, raised high,
#rows scanned with pulldown input.


import board
import time
import digitalio


test = digitalio.DigitalInOut(board.GP28)  #pin_obj is an internal variable
test.direction = digitalio.Direction.OUTPUT



test_out = digitalio.DigitalInOut(board.GP11)  # C pin out
test_out.direction = digitalio.Direction.OUTPUT
   
test_in = digitalio.DigitalInOut(board.GP19)  #octave 4
test_in.direction = digitalio.Direction.INPUT
test_in.pull = digitalio.Pull.DOWN
    
test_out.value = True

