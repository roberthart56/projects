
#scan_matrix_play_61 notes
#columns are attached to outputs, raised high,
#rows scanned with pulldown input.


import board
import time
import digitalio
import usb_midi
import adafruit_midi
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff

test = digitalio.DigitalInOut(board.GP28)  #pin_obj is an internal variable
test.direction = digitalio.Direction.OUTPUT

midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)


col_pin = [board.GP11, board.GP10, board.GP9, board.GP8, board.GP7, board.GP6, board.GP5, board.GP4, board.GP3, board.GP2, board.GP1, board.GP0]
row_pin = [board.GP16, board.GP17, board.GP18, board.GP19, board.GP20, board.GP21 ]

col = []		#list of configured objects for columns
row = []		#list of configured objects for rows


for pin in (col_pin):			#set up columns
    pin_obj = digitalio.DigitalInOut(pin)  #pin_obj is an internal variable
    pin_obj.direction = digitalio.Direction.OUTPUT
    col.append(pin_obj)

for pin in (row_pin):			#set up rows
    pin_obj = digitalio.DigitalInOut(pin)  
    pin_obj.direction = digitalio.Direction.INPUT
    pin_obj.pull = digitalio.Pull.DOWN
    row.append(pin_obj)
    


