
#scan_matrix_play_61 notes
#columns are attached to outputs, raised high,
#rows scanned with pulldown input.

import microcontroller
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


col_pin = [board.GP0, board.GP1, board.GP2, board.GP3, board.GP4, board.GP5, board.GP6, board.GP7, board.GP8, board.GP9, board.GP10, board.GP11]
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
    
note = [[36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47],
        [48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59],
        [60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71],
        [72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83],
        [84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95],
        [96, None, None, None, None, None, None, None, None, None, None, None]]
num_rows = len(row)
num_cols = len(col)

old = [[0 for _ in range(num_cols)] for _ in range(num_rows)]

def scan_matrix(c,r):
    a=[[0 for _ in range(len(col))] for _ in range(len(row))]
    for i, el in enumerate(c):
        el.value = True
        #microcontroller.delay_us(100)
        for j, element in enumerate(r):
            a[j][i]=element.value
        el.value = False
    return(a)

while True:
    test.value = True
    new = scan_matrix(col,row)
    test.value = False 
    if not new==old:
        for i in range(num_rows):
            for j in range(num_cols):
                if old[i][j] == False and new[i][j] == True:
                    print(note[i][j], 'on')
                    midi.send(NoteOn(note[i][j], 127))
                elif old[i][j] == True and new[i][j] == False:
                    print(note[i][j], 'off')
                    midi.send(NoteOff(note[i][j], 127))
    
        old = new
      
#main



